from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_view, name="landing"),                       # Landing Page
    path("about/", views.about_view, name="about"),                     # About
    path("dashboard/", views.dashboard_view, name="dashboard"),         # Dashboard (Protected)
    path("screening/", views.screening_view, name="screening"),         # Screening
    path("login/", views.login_view, name="login"),                     # Login
    path("register/", views.register_view, name="register"),            # Register
    path("logout/", views.logout_view, name="logout"),                  # Logout
    path("contact/", views.contact_view, name="contact"),               # Contact
    path("faq/", views.faq_view, name="faq"),                           # FAQ
    path("api/ai-answer/", views.ai_answer, name="ai_answer"),
    path("api/trigger-ai/", views.trigger_ai_for_item, name="trigger_ai"),  # Trigger AI from dashboard
]
