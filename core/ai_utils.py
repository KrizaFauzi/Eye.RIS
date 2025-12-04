# core/ai_utils.py
import json
from typing import Tuple

from langchain_groq import ChatGroq
from django.conf import settings

# buat instance LLM module-level (reuse)
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.1,
    max_tokens=2048,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)

def ask_ai(variable: str, question: str, system_prompt: str = None) -> Tuple[str, dict]:
    """
    Memanggil LLM dan mengembalikan (answer_text, raw_response).
    - variable: string yang ingin kamu masukkan ke prompt
    - question: pertanyaan user/trigger
    - system_prompt: jika None pakai default
    """
    if system_prompt is None:
        system_prompt = "Kamu adalah seorang yang paham tentang medis, khususnya tentang diagnostik penyakit mata."

    # Susun messages sesuai pattern yang kamu pakai
    messages = [
        ("system", system_prompt),
        ("human", f"Saya punya variabel: `{variable}`. Pertanyaan: {question}. Jawab fokus pada `{variable}`.")
    ]

    # panggil LLM (synchronous)
    resp = llm.invoke(messages)

    # extract content jika ada attribute content, fallback ke str(resp)
    answer = getattr(resp, "content", None)
    if answer is None:
        # kadang SDK mengembalikan dict-like; coba dump
        try:
            answer = json.dumps(resp)
        except Exception:
            answer = str(resp)

    # return jawaban dan raw resp supaya caller bisa log / simpan metadata
    return answer, resp


def analyze_eye_prediction(patient_name: str, patient_age: int, patient_gender: str, prediction: str) -> str:
    """
    Analisis hasil prediksi penyakit mata menggunakan AI.
    - patient_name: nama pasien
    - patient_age: umur pasien
    - patient_gender: jenis kelamin pasien
    - prediction: hasil prediksi dari model (format: "Mata Kiri: ...\nMata Kanan: ...")
    
    Returns: string analisis dari AI
    """
    system_prompt = (
        "Kamu adalah asisten medis ahli dalam diagnostik mata. "
        "Berdasarkan hasil deteksi penyakit mata dari model AI, "
        "berikan penjelasan singkat tentang kondisi mata pasien, rekomendasi, dan saran tindak lanjut. "
        "Jawab dalam bahasa Indonesia, singkat dan jelas."
        "Jangan halu dan katakan jika informasi tidak cukup."
        "Jika hasilnya other disease, jelaskan bahwa hasilnya tidak spesifik dan sarankan pemeriksaan lebih lanjut."
        "Jangan gunakan format markdown dalam jawaban."
        "Gunakan format yang simpel dalam jawaban."
    )
    
    question = (
        f"Pasien dengan data: Nama={patient_name}, Umur={patient_age}, Gender={patient_gender}. "
        f"Hasil deteksi dari model:\n{prediction}\n"
        f"Berikan analisis dan rekomendasi medis untuk hasil deteksi ini."
    )
    
    answer, _ = ask_ai(variable=prediction, question=question, system_prompt=system_prompt)
    return answer
