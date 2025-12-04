from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'image1', 'image2']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nama Pasien', 'class': 'form-input'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Umur', 'class': 'form-input', 'min': 0}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        img1 = cleaned.get('image1')
        img2 = cleaned.get('image2')
        if not img1 or not img2:
            raise ValidationError('Dua gambar harus diupload.')
        return cleaned


class LoginForm(forms.Form):
    """Form untuk login user"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'login-input'
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'login-input'
        }),
        label='Password'
    )


class RegisterForm(UserCreationForm):
    """Form untuk register user baru"""
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nama depan',
            'class': 'login-input'
        }),
        label='Nama Depan'
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nama belakang',
            'class': 'login-input'
        }),
        label='Nama Belakang'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'login-input'
        }),
        label='Email'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'login-input'
        }),
        label='Password',
        help_text=None
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Konfirmasi Password',
            'class': 'login-input'
        }),
        label='Konfirmasi Password',
        help_text=None
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        """Validasi email tidak boleh duplikat"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email ini sudah terdaftar. Silahkan gunakan email lain.')
        return email

    def clean_password2(self):
        """Validasi password match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Password tidak cocok.')
        return password2

    def save(self, commit=True):
        """Override save untuk set username dari email"""
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Set username sama dengan email
        if commit:
            user.save()
        return user
