from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.cache import cache  # Use Django's cache to store OTPs temporarily

def send_welcome_email(user_email, username):
    """Send a welcome email to the user."""
    subject = "Welcome to Bills Manager!"
    message = f"Hi {username},\n\nThank you for verifying your account with Bills Manager. We're excited to have you on board!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)


def generate_otp(user_email):
    """Generate a 6-digit OTP and store it in the cache."""
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    cache.set(f"otp_{user_email}", otp, timeout=300)  # Store OTP in cache for 5 minutes
    return otp

def send_otp_email(user_email):
    """Send an OTP email to the user."""
    otp = generate_otp(user_email)
    subject = "Your OTP for Bills Manager"
    message = f"Your OTP is: {otp}\n\nPlease use this to verify your account. This OTP is valid for 5 minutes."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
    


