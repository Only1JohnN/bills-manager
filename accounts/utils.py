# utils.py

import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_otp(user_email):
    otp = str(random.randint(100000, 999999))
    cache.set(user_email, otp, timeout=300)  # 5 minutes
    return otp

def verify_otp(user_email, otp):
    cached_otp = cache.get(user_email)
    return cached_otp == otp

def send_otp_email(user_email, username):
    otp = generate_otp(user_email)
    subject = 'Your OTP Code'
    message = render_to_string('emails/otp_email.html', {'otp': otp, 'username': username})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

def send_reset_password_email(user):
    otp = generate_otp(user.email)
    subject = 'Password Reset OTP'
    message = render_to_string('password_reset_email.html', {'otp': otp, 'username': user.username})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_password_reset_success_email(user_email, username):
    subject = 'Password Reset Successful'
    message = render_to_string('password_reset_success_email.html', {'username': username})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
