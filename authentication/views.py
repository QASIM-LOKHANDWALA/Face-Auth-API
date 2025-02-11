from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .face_utils import register_face, verify_face
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
import base64
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import os

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data["username"]
            password = request.data["password"]
            face_image = request.data["face_image"]
            
            image_data = base64.b64decode(face_image.split(",")[1])
            
            face_id = register_face(image_data, username)
            if not face_id:
                return Response({"error": "Face not detected or registration failed"}, status=400)

            user = User(
                username=username,
                password=make_password(password),
                face_id=face_id
            )
            user.save()
            
            return Response({
                "message": "User registered successfully",
                "face_id": face_id
            }, status=201)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data["username"]
            face_image = request.data["face_image"]

            image_data = base64.b64decode(face_image.split(",")[1])

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

            is_match = verify_face(image_data, username)
            
            if is_match:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                })
            else:
                return Response({"error": "Face verification failed"}, status=401)
                
        except Exception as e:
            return Response({"error": str(e)}, status=400)