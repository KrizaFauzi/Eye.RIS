from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, RegisterForm, PatientForm
from .models import Patient
import numpy as np
from PIL import Image
import io
import os
import joblib
# ensure custom keras layers used in the pickled model are registered
from . import model_custom
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .ai_utils import ask_ai, analyze_eye_prediction
from django.views.decorators.http import require_POST
import markdown


# import ChatGroq dari langchain-groq
from langchain_groq import ChatGroq

# Mapping indeks prediksi ke nama penyakit
DISEASE_LABELS = {
    0: "Normal",
    1: "Diabetes",
    2: "Glaucoma",
    3: "Cataract",
    4: "Age related Macular Degeneration",
    5: "Hypertension",
    6: "Pathological Myopia",
    7: "Other diseases/abnormalities"
}


def home(request):
    return HttpResponse("Halo, ini halaman pertama Django!")


def landing_view(request):
    return render(request, "core/landing.html", {"page": "landing"})


def about_view(request):
    return render(request, "core/about.html", {"page": "about"})


@login_required(login_url='login')
def dashboard_view(request):
    """Dashboard - Hanya untuk user yang sudah login"""
    prediction = None
    # Analisis hasil prediksi menggunakan AI
    ai_analysis = None
    try:
        ai_raw = analyze_eye_prediction(
            patient_name=patient.name,
            patient_age=patient.age,
            patient_gender=patient.gender,
            prediction=prediction
        )
        # Convert markdown → HTML
        ai_analysis = markdown.markdown(ai_raw, extensions=["extra"])
    except Exception as e:
        ai_analysis = f"<p><strong>AI Analysis Error:</strong> {str(e)}</p>"
        form = PatientForm()

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            # simpan instance tanpa commit dulu untuk dapatkan file paths
            patient = form.save(commit=False)
            patient.save()

            # proses gambar: buka kedua image, konversi ke numpy array
            imgs = []
            for field in ('image1', 'image2'):
                img_field = getattr(patient, field)
                if img_field:
                    # buka file dari storage
                    img_path = img_field.path
                    with Image.open(img_path) as im:
                        # convert to RGB and resize to 224x224 as requested
                        im = im.convert('RGB')
                        try:
                            resample = Image.LANCZOS
                        except Exception:
                            # Pillow older versions
                            resample = Image.ANTIALIAS
                        im = im.resize((224, 224), resample=resample)
                        arr = np.array(im)
                        imgs.append(arr)

            if len(imgs) < 2:
                messages.error(request, 'Gagal memproses gambar. Pastikan kedua gambar diupload.')
            else:
                # stack arrays
                stacked = np.stack(imgs, axis=0)

                # load model (lazy)
                model_path = os.path.join(os.path.dirname(__file__), 'model', 'model_1.pkl')
                try:
                    clf = joblib.load(model_path)
                except Exception:
                    # fallback to pickle
                    import pickle

                    with open(model_path, 'rb') as f:
                        clf = pickle.load(f)

                # predict — depending on model expected shape, adjust if necessary
                try:
                    hasil_prediksi = clf.predict(stacked)
                    # Jika model mengembalikan probabilitas (mis. shape (n, num_classes)),
                    # ambil argmax sepanjang axis=1.
                    try:
                        if hasattr(hasil_prediksi, 'ndim') and hasil_prediksi.ndim > 1 and hasil_prediksi.shape[-1] > 1:
                            y_pred = np.argmax(hasil_prediksi, axis=1)
                            # Konversi indeks ke nama penyakit dengan label mata kiri/kanan
                            disease_left = DISEASE_LABELS.get(int(y_pred[0]), f"Unknown ({y_pred[0]})")
                            disease_right = DISEASE_LABELS.get(int(y_pred[1]), f"Unknown ({y_pred[1]})") if len(y_pred) > 1 else "N/A"
                            prediction = f"Mata Kiri: {disease_left}\nMata Kanan: {disease_right}"
                        else:
                            # jika sudah berupa label 1D
                            if hasattr(hasil_prediksi, 'ndim') and hasil_prediksi.ndim == 1:
                                # Asumsikan ini adalah indeks, konversi ke nama penyakit
                                disease_names = [DISEASE_LABELS.get(int(val), f"Unknown ({val})") for val in hasil_prediksi.tolist()]
                                disease_left = disease_names[0] if len(disease_names) > 0 else "N/A"
                                disease_right = disease_names[1] if len(disease_names) > 1 else "N/A"
                                prediction = f"Mata Kiri: {disease_left}\nMata Kanan: {disease_right}"
                            else:
                                prediction = str(hasil_prediksi)
                    except Exception:
                        # fallback stringify
                        prediction = str(hasil_prediksi)
                except Exception as e:
                    prediction = f'Error saat prediksi: {e}'

                # Analisis hasil prediksi menggunakan AI
                ai_analysis = None
                try:
                    ai_analysis = analyze_eye_prediction(
                        patient_name=patient.name,
                        patient_age=patient.age,
                        patient_gender=patient.gender,
                        prediction=prediction
                    )
                except Exception as e:
                    ai_analysis = f"AI Analysis Error: {str(e)}"

                # simpan prediction ke instance
                patient.prediction = prediction
                patient.save()

    return render(request, "core/dashboard.html", {"page": "dashboard", "form": form, "prediction": prediction, "ai_analysis": ai_analysis})


def screening_view(request):
    return render(request, "core/screening.html", {"page": "screening"})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """View untuk login user"""
    # Jika user sudah login, redirect ke dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate menggunakan email (username set dari email)
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Selamat datang kembali, {user.first_name or email}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Email atau password salah. Silahkan coba lagi.')
    else:
        form = LoginForm()
    
    return render(request, "core/login.html", {
        "page": "login",
        "form": form
    })


@require_http_methods(["GET", "POST"])
def register_view(request):
    """View untuk register user baru"""
    # Jika user sudah login, redirect ke dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Setelah berhasil register, arahkan ke halaman login (user harus login manual)
            messages.success(request, 'Akun berhasil dibuat. Silakan masuk menggunakan email dan password Anda.')
            return redirect('login')
        else:
            # Tampilkan error dari form
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegisterForm()
    
    return render(request, "core/register.html", {
        "page": "register",
        "form": form
    })


def contact_view(request):
    # nanti bisa diisi logic contact user
    return render(request, "core/contact.html", {"page": "contact"})


def faq_view(request):
    # nanti bisa diisi logic faq user
    return render(request, "core/faq.html", {"page": "faq"})


@require_http_methods(["POST"])
def logout_view(request):
    """View untuk logout user"""
    logout(request)
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('landing')

@csrf_exempt
def ai_answer(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")
    variable = body.get("variable", "")
    question = body.get("question", "")
    if not question:
        return HttpResponseBadRequest("`question` is required")

    try:
        answer, raw = ask_ai(variable, question)
        return JsonResponse({"answer": answer})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@require_POST
@login_required
def trigger_ai_for_item(request):
    """
    Contoh: trigger AI dari backend (misal: user klik tombol 'Analyze' di dashboard)
    Body JSON: { "variable": "...", "question": "..." }
    """
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    variable = body.get("variable", "")
    question = body.get("question", "")
    if not question:
        return HttpResponseBadRequest("`question` required")

    answer, raw = ask_ai(variable, question)

    html_answer = markdown(answer, extensions=["extra"])

    return JsonResponse({"status": "ok", "answer": html_answer})