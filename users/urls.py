from django.urls import path

<<<<<<< HEAD
from .views import SignUpAPIView, VerifyAPIView

urlpatterns = [
    path('signup/', SignUpAPIView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
=======
from .views import SignUpAPIView


urlpatterns = [
    path('signup/', SignUpAPIView.as_view()),
>>>>>>> origin/master
]
