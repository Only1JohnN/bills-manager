# accounts/serializers.py

from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True, help_text="Enter a unique username.")
    first_name = serializers.CharField(max_length=100, required=True, help_text="Enter your first name.")
    last_name = serializers.CharField(max_length=100, required=True, help_text="Enter your last name.")
    email = serializers.EmailField(required=True, help_text="Enter a valid email address.")
    phone_number = serializers.CharField(max_length=15, required=True, help_text="Enter a valid phone number.")
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password], help_text="Enter a strong password.")
    confirm_password = serializers.CharField(write_only=True, required=True, help_text="Re-enter your password.")

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password', 'confirm_password']

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({'error': 'Invalid credentials'})

            if not user.check_password(password):
                raise serializers.ValidationError({'error': 'Invalid credentials'})

            if not user.is_active:
                raise serializers.ValidationError({'error': 'User account is disabled.'})

            data['user'] = user
            return data
        else:
            raise serializers.ValidationError({'error': 'Email and password are required.'})
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    # phone_number = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('email'): # and not data.get('phone_number'):
            raise serializers.ValidationError("Either email or phone number is required.")
        return data