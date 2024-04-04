from django.urls import path

from .views import SignUpAPIView, VerifyAPIView

urlpatterns = [
    path('signup/', SignUpAPIView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
]
