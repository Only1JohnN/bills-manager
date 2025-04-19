from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
from django.conf import settings
import random
from django.core.cache import cache


def generate_otp(user_email):
    otp = random.randint(100000, 999999)
    cache.set(f"otp_{user_email}", otp, timeout=300)  # 5 mins
    return otp


def send_otp_email(user_email):
    """Send an OTP email to the user."""
    otp = generate_otp(user_email)
    subject = "Your OTP for Bills Manager"
    html_content = render_to_string(
        'emails/otp_email.html',
        {'otp': otp, 'year': datetime.now().year}
    )
    plain_text_content = f"Your OTP is: {otp}\n\nPlease use this to verify your account. This OTP is valid for 5 minutes."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, plain_text_content, from_email, recipient_list, html_message=html_content)


def send_welcome_email(user_email, username):
    """Send a welcome email to a new user."""
    subject = "Welcome to Bills Manager!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_email]

    text_content = f"Hi {username}, welcome to Bills Manager!"
    html_content = render_to_string(
        "emails/welcome_email.html",
        {"username": username, "year": datetime.now().year}
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
