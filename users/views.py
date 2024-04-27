from datetime import datetime

from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User, NEW, CODE_VERIFIED
from rest_framework import generics, permissions, status

from .serializers import SignUpSerializer, UserInfoUpdateSerializer, LoginSerializer, RefreshTokenSerializer, \
    UserPhotoChangeSerializer, LogOutSerializer, VerifySerializer


class SignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]


class VerifyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = VerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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


class UserInfoUpdateView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserInfoUpdateSerializer
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(UserInfoUpdateView, self).update(request, *args, **kwargs)
        user = self.get_object()
        data = {
            'success': True,
            'message': "Ma'lumotlaringiz kiritildi!",
            'auth_status': user.auth_status
        }
        data.update(user.token())
        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        super(UserInfoUpdateView, self).partial_update(request, *args, **kwargs)
        user = self.get_object()
        data = {
            'success': True,
            'message': "Ma'lumotlaringiz kiritildi!",
            'auth_status': user.auth_status
        }
        data.update(user.token())
        return Response(data)


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer


class RefreshTokenView(TokenRefreshView):
    serializer_class = RefreshTokenSerializer


class UserPhotoUpdateView(UpdateAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = UserPhotoChangeSerializer
    queryset = User.objects.all()
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(UserPhotoUpdateView, self).update(request, *args, **kwargs)
        user = self.get_object()
        data = {
            'success': True,
            'message': "Foydalanuvchi rasmi o'zgartirildi",
            'auth_status': user.auth_status
        }
        data.update(user.token())
        return Response(data, status=status.HTTP_200_OK)


class LogOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LogOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                'success': True,
                'message': "Siz tizimdan chiqdingiz!"
            }
            return Response(data, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


