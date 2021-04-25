from django.contrib.auth import get_user_model
from rest_framework import serializers

class SignUpSerializer(serializers.Serializer):    
    email = serializers.EmailField(max_length=255)
    password1 = serializers.CharField(max_length=128)
    password2 = serializers.CharField(max_length=128)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)

class LogInSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)
    