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
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user