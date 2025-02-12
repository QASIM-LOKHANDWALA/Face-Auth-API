from django.urls import path
from .views import RegisterView, LoginView, AuthUIView
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("verify_token/", TokenVerifyView.as_view(), name="verify_token"),
    path("authUI/", AuthUIView.as_view(), name="auth_ui"),
]