# accounts/urls.py

from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, ForgotPasswordView, VerifyOTPView, 
    VerifyPasswordOTPView, ResetPasswordView, ResendOTPView, FundWalletView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    
    path('logout/', LogoutView.as_view(), name='logout'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-password-otp/', VerifyPasswordOTPView.as_view(), name='verify_password_otp'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset_password'),
]
