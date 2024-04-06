<<<<<<< HEAD
from datetime import datetime

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .models import User, NEW, CODE_VERIFIED
=======
from django.shortcuts import render
from rest_framework import generics, permissions

from .models import User
>>>>>>> origin/master
from .serializers import SignUpSerializer


class SignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]
<<<<<<< HEAD


class VerifyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        data = {
            "success": True,
            "auth_status": user.auth_status,
        }
        data.update(user.token())
        return Response(data)

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_code.filter(code=code, expiration_time__gte=datetime.now(), is_confirmed=False)
        print(verifies)
        if not verifies.exists():
            data = {"message": "Tasdiqlash kodi xato yoki eskirgan"}
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True
=======
>>>>>>> origin/master
