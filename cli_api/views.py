from django.core import exceptions
from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
import django.contrib.auth.password_validation as validators

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignUpSerializer, LogInSerializer

class SignUp(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            password1 = serializer.data['password1']
            password2 = serializer.data['password2']
            first_name = serializer.data['first_name']
            last_name = serializer.data['last_name']

            password_mismatch = dict()
            if password1 != password2:
                password_mismatch = {'error': "Your passwords don't match"}
                return Response(password_mismatch, status=status.HTTP_400_BAD_REQUEST)

            errors = dict()
            try:
                validators.validate_password(password=password1, user=email)

            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)

            if errors:                
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            user = get_user_model().objects.create_user(email=email, password=password1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()            

            content = { 'email': email, 'first_name': first_name,
                       'last_name': last_name 
                       }

            return Response(content, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogIn(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LogInSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            user = authenticate(email=email, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)
                content = { 'token': token.key }

                return Response(content, status=status.HTTP_200_OK)
            else:
                content = { 'email': email }

                return Response(content, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)