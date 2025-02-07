from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .face_utils import extract_face_embedding, compare_embeddings
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
import base64
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]
        face_image = request.data["face_image"]

        image_data = base64.b64decode(face_image.split(",")[1])
        image_path = f"temp/{username}.jpg"
        with open(image_path, "wb") as f:
            f.write(image_data)

        embedding = extract_face_embedding(image_path)
        if not embedding:
            return Response({"error": "Face not detected"}, status=400)

        user = User(username=username, password=make_password(password), face_embedding=embedding)
        user.save()
        return Response({"message": "User registered successfully"}, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data["username"]
        face_image = request.data["face_image"]

        image_data = base64.b64decode(face_image.split(",")[1])
        image_path = f"temp/{username}.jpg"
        with open(image_path, "wb") as f:
            f.write(image_data)

        embedding = extract_face_embedding(image_path)
        if not embedding:
            return Response({"error": "Face not detected"}, status=400)

        try:
            user = User.objects.get(username=username)
            if compare_embeddings(embedding, user.face_embedding):
                refresh = RefreshToken.for_user(user)
                return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
            else:
                return Response({"error": "Face mismatch"}, status=401)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
