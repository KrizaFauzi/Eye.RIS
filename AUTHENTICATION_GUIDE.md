# 🔐 Authentication System - Eye.IRIS

## Overview
Sistem authentication lengkap untuk login dan register dengan Django built-in User model.

---

## 📁 File Structure

### Backend Files
```
core/
├── forms.py (NEW)           # LoginForm dan RegisterForm
├── views.py (UPDATED)       # Login/Register/Logout logic
└── urls.py (UPDATED)        # Route untuk logout
```

### Frontend Files
```
templates/
├── core/
│   ├── login.html (UPDATED)     # Login form dengan error handling
│   └── register.html (UPDATED)  # Register form dengan validation
└── partials/
    └── header.html (UPDATED)    # User greeting dan logout button
```

### Configuration
```
iris/settings.py (UPDATED)      # LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL
static/css/main.css (UPDATED)   # Alert styles dan form error styles
```

---

## 🔑 Authentication Flow

### Login Process
1. User mengakses `/login/`
2. Form validation di `LoginForm`
3. Django authenticate dengan username (email) dan password
4. Jika berhasil → redirect ke dashboard dengan success message
5. Jika gagal → menampilkan error message

### Register Process
1. User mengakses `/register/`
2. Form validation di `RegisterForm`
3. Check duplikasi email
4. Check password match
5. Create user dengan `username = email`
6. Auto-login setelah register
7. Redirect ke dashboard dengan success message

### Logout Process
1. User klik tombol Logout
2. POST request ke `/logout/`
3. Session dihapus
4. Redirect ke landing page

---

## 🛡️ Features

### 1. Login Form (`LoginForm`)
- Input: Email, Password
- Validation: Email format, Required fields
- Error handling: Email/password tidak cocok

### 2. Register Form (`RegisterForm`)
- Extend Django `UserCreationForm`
- Input: First Name, Last Name, Email, Password, Confirm Password
- Validation:
  - Email harus unik
  - Password harus cocok
  - Password strength validators (built-in Django)
- Username otomatis set dari email

### 3. Views Protection
- `dashboard_view` dilindungi dengan `@login_required`
- Auto-redirect ke login jika belum authenticated
- Post-login redirect ke dashboard
- Post-logout redirect ke landing page

### 4. User Experience
- Dynamic header (show name ketika login)
- Success/error messages dengan styling
- Password toggle functionality
- Responsive mobile menu
- CSRF protection

---

## 🧪 Testing

### Test Cases

#### Register Flow
```
1. Buka http://localhost:8000/register/
2. Isi form:
   - Nama Depan: John
   - Nama Belakang: Doe
   - Email: john@example.com
   - Password: SecurePass123
   - Konfirmasi: SecurePass123
3. Klik "Daftar"
4. Harus auto-login dan redirect ke /dashboard/
```

#### Login Flow
```
1. Logout dulu atau buka incognito tab
2. Buka http://localhost:8000/login/
3. Isi form:
   - Email: john@example.com
   - Password: SecurePass123
4. Klik "Masuk"
5. Harus redirect ke /dashboard/
```

#### Error Cases
```
1. Email duplikat → Error message di register
2. Password tidak cocok → Error message di register
3. Email/password salah → Error message di login
4. Akses /dashboard tanpa login → Redirect ke login
```

---

## 📝 Database

### User Model (Django Built-in)
```python
- id (PK)
- username (unique) → di-set dari email
- email (unique)
- first_name
- last_name
- password (hashed)
- is_active
- is_staff
- is_superuser
- date_joined
- last_login
```

### Sessions
- Automatically managed oleh Django
- Stored di database (contrib.sessions)
- CSRF token di-generate per form

---

## 🔄 URL Routes

| URL | View | Method | Auth Required |
|-----|------|--------|---------------|
| `/login/` | login_view | GET, POST | No |
| `/register/` | register_view | GET, POST | No |
| `/logout/` | logout_view | POST | Yes |
| `/dashboard/` | dashboard_view | GET | **Yes** |

---

## 🚀 Next Steps

1. **Forget Password**
   - Buat forgot_password_view
   - Email verification dengan token
   - Reset password form

2. **Email Verification**
   - Send verification email saat register
   - Activate account setelah verify

3. **Social Authentication**
   - Google OAuth
   - GitHub OAuth
   - Facebook OAuth

4. **User Profile**
   - Profile page
   - Edit profile
   - Change password

5. **Admin Panel**
   - Register User model di admin.py
   - Custom user admin display

---

## ⚙️ Configuration Details

### Settings.py
```python
# Authentication URLs
LOGIN_URL = 'login'                    # Redirect jika tidak login
LOGIN_REDIRECT_URL = 'dashboard'       # Redirect setelah login
LOGOUT_REDIRECT_URL = 'landing'        # Redirect setelah logout
```

### Middleware (Already Configured)
```python
django.contrib.auth.middleware.AuthenticationMiddleware
django.contrib.sessions.middleware.SessionMiddleware
```

### Installed Apps (Already Configured)
```python
'django.contrib.auth'
'django.contrib.contenttypes'
'django.contrib.sessions'
```

---

## 🎨 CSS Classes

### Messages/Alerts
- `.alert` - Base alert class
- `.alert-success` - Green alert (success messages)
- `.alert-error` - Red alert (error messages)
- `.alert-warning` - Yellow alert (warning messages)

### Form Elements
- `.login-form-group` - Form field container
- `.error-text` - Error message display
- `.password-toggle` - Password input with toggle button

---

## 📌 Important Notes

1. **Username & Email**
   - Username otomatis di-set dari email
   - User login menggunakan email (bukan username)
   - Tidak bisa ada dua user dengan email sama

2. **Password Security**
   - Hashed dengan PBKDF2 (default Django)
   - Minimum length validators
   - Common password validators
   - User attribute similarity validators

3. **CSRF Protection**
   - `{% csrf_token %}` di semua POST forms
   - Automatic validation oleh Django middleware

4. **Messages Framework**
   - Menggunakan Django messages framework
   - Display di template dengan `{% if messages %}`
   - Auto-clear setelah di-render

---

**Created:** December 4, 2025
**Last Updated:** December 4, 2025
