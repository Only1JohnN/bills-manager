from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True, help_text="Enter a unique username.")
    email = serializers.EmailField(required=True, help_text="Enter a valid email address.")
    first_name = serializers.CharField(max_length=100, required=True, help_text="Enter your first name.")
    last_name = serializers.CharField(max_length=100, required=True, help_text="Enter your last name.")
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password],help_text="Enter a strong password.")
    confirm_password = serializers.CharField(write_only=True, required=True, help_text="Re-enter your password.")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password', 'confirm_password']

    def validate_username(self, value):
        """Ensure the username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_email(self, value):
        """Ensure the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_phone_number(self, value):
        """Ensure the phone number is unique."""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True, help_text="Enter your username.")
    password = serializers.CharField(write_only=True, required=True, help_text="Enter your password.")
    
    class Meta:
        fields = ['username', 'password']
    
    def validate(self, attrs):
        if not User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "User does not exist."})
        return attrs
    def validate_password(self, value):
        """Ensure the password is correct."""
        user = User.objects.filter(username=self.initial_data['username']).first()
        if user and not user.check_password(value):
            raise serializers.ValidationError("Incorrect password or username.")
        return value