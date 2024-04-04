from django.shortcuts import render
from rest_framework import generics, permissions

from .models import User
from .serializers import SignUpSerializer


class SignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]
