from django.urls import path

from .views import SignUpAPIView, VerifyAPIView, UserInfoUpdateView, LoginView, RefreshTokenView, UserPhotoUpdateView, \
    LogOutView

urlpatterns = [
    path('signup/', SignUpAPIView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('user-change/', UserInfoUpdateView.as_view()),
    path('login/', LoginView.as_view(), name='token_obtain'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('user-photo-change/', UserPhotoUpdateView.as_view()),
    path('logout/', LogOutView.as_view()),
]
