from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("kyc/", views.kyc_submit, name="kyc_submit"),
    path("kyc/aadhaar/", views.aadhaar_otp_request, name="aadhaar_otp_request"),
    path("kyc/aadhaar/verify/", views.aadhaar_otp_verify, name="aadhaar_otp_verify"),
]
