from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import RegisterSerializer
from django.contrib.auth.models import User
from .utils import send_welcome_email, send_otp_email
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  # Mark user as inactive until OTP is verified
            user.save()

            # Send OTP email
            send_otp_email(user.email)

            return Response({"message": "User registered successfully. An OTP has been sent to your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the OTP from the cache
        cached_otp = cache.get(f"otp_{email}")
        if cached_otp is None:
            return Response({"error": "OTP has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if str(cached_otp) != str(otp):
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Activate the user
        try:
            user = User.objects.get(email=email)
            user.is_active = True
            user.is_verified = True
            user.save()
            
            # Send a welcome email after successful verification
            send_welcome_email(user.email, user.username)
            
            # Optionally delete the OTP from cache after successful verification
            cache.delete(f"otp_{email}")
            return Response({"message": "OTP verified successfully. Your account is now active."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)