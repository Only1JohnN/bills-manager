# accounts/views.py

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializer import RegisterSerializer, LoginSerializer, ResendOTPSerializer
import requests
import uuid
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import (
    send_otp_email, verify_otp, send_reset_password_email,
    send_password_reset_success_email, send_welcome_email,
    build_payment_payload
)

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    http_method_names =['post']

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user.email, user.username)
            return Response(
                {'message': 'OTP sent to your email for verification'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    http_method_names =['post']

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        if verify_otp(email, otp):
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.is_email_verified = True  # Mark email as verified
                user.save()
                
                # Send a welcome email after successful verification
                send_welcome_email(user.email, user.username)
            
                return Response({'message': 'Account verified successfully'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    
class ResendOTPView(APIView):
    http_method_names =['post']
    
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            # phone_number = serializer.validated_data.get('phone_number') # If using phone
            
            if email:
                try:
                    user = User.objects.get(email=email)
                    send_otp_email(email, user.username)  # Use your utility function
                    return Response({"message": "New OTP has been sent to your email."}, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
                
            # elif phone_number:
            #     try:
            #         user = User.objects.get(phone_number=phone_number)
            #         send_otp_phone_number(phone_number, user.username)  # Use your utility function
            #         return Response({"message": "New OTP has been sent to your email."}, status=status.HTTP_200_OK)
            #     except User.DoesNotExist:
            #         return Response({"error": "User with this Phone Number does not exist."}, status=status.HTTP_404_NOT_FOUND)
                

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    http_method_names =['post']

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'email': user.email,
                    'phone_number': getattr(user, 'phone_number', None),
                    'is_active': user.is_active,
                    'date_joined': user.date_joined,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'is_email_verified': getattr(user, 'is_email_verified', None),
                    'is_phone_verified': getattr(user, 'is_phone_verified', None),
                    'is_verified': getattr(user, 'is_verified', None),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    http_method_names =['post']

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            send_reset_password_email(user)
            return Response({'message': 'Password reset OTP sent to your email'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)


class VerifyPasswordOTPView(APIView):
    permission_classes = [AllowAny]
    http_method_names =['post']

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        if verify_otp(email, otp):
            try:
                user = User.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                return Response({'uid': uid, 'token': token}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    http_method_names =['post']

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            password = request.data.get('password')
            if not password:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

            user.password = make_password(password)
            user.save()

            send_password_reset_success_email(user.email, user.username)
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names =['post']
    
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout Successful.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class FundWalletView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PaymentFundingSerializer(data=request.data)
        if serializer.is_valid():
            # Validate the request data
            amount = serializer.validated_data['amount']
            email = serializer.validated_data['email']
            phone_number = serializer.validated_data['phone_number']
            name = serializer.validated_data['name']
            
            # Create a transaction entry for the funding
            tx_ref = str(uuid.uuid4())  # Generate a unique transaction reference
            transaction = Transaction.objects.create(
                user=request.user, 
                tx_ref=tx_ref,
                amount=amount,
                status='pending'  # Initially set to pending
            )
            
            # Build the payload for Flutterwave
            payload = build_payment_payload(request.user, tx_ref, amount, email, phone_number, name)
            headers = {
                "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
                "Content-Type": "application/json"
            }

            # Send request to Flutterwave to initiate payment
            response = requests.post(
                f"{settings.FLW_BASE_URL}/charges?tx_ref={tx_ref}",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                payment_link = response.json().get("data", {}).get("link", "")
                if payment_link:
                    # Update the transaction with the correct link for user redirection
                    transaction.status = "pending"
                    transaction.save()
                    return Response({"payment_url": payment_link}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Error processing payment link."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)