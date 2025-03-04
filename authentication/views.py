from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .face_utils import register_face, verify_face
from django.contrib.auth.hashers import make_password
import base64
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User        
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data["username"]
            password = request.data["password"]
            face_image = request.data["face_image"]
            
            print("Username:", username)
            print("Face image length:", len(face_image) if face_image else "No image")
            
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
            print("Registration error:", str(e))
            return Response({"error": str(e)}, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data["username"]
            face_image = request.data["face_image"]
            
            print(f"login for user: {username}")

            image_data = base64.b64decode(face_image.split(",")[1])

            try:
                user = User.objects.get(username=username)
                print(f"User found: {user.username}")
            except User.DoesNotExist:
                print(f"User not found: {username}")
                return Response({"error": "User not found"}, status=404)

            is_match = verify_face(image_data, username)
            print(f"verification result: {is_match}")
            
            if is_match:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                })
            else:
                return Response({"error": "Face verification failed"}, status=401)
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return Response({"error": str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class AuthUIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        redirect_url = request.GET.get("redirect_url", "")
        if not redirect_url:
            return Response({"error": "Missing redirect_url"}, status=400)
        request.session["redirect_url"] = redirect_url
        return render(request, "auth/index.html")
    
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get("username")
            face_image = request.data.get("face_image")
            redirect_url = request.session.get("redirect_url")

            if not all([username, face_image, redirect_url]):
                return Response({"error": "Missing required parameters"}, status=400)

            try:
                image_data = base64.b64decode(face_image.split(",")[1])
            except:
                return Response({"error": "Invalid face image format"}, status=400)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

            is_match = verify_face(image_data, username)
            if not is_match:
                return Response({"error": "Face verification failed"}, status=401)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            final_redirect_url = f"{redirect_url}?token={access_token}"
            print("Redirecting to:", final_redirect_url)
            return redirect(final_redirect_url)

        except Exception as e:
            return Response({"error": str(e)}, status=400)