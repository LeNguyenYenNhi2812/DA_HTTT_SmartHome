# users/views.py

from django.http import JsonResponse  # type: ignore # Import JsonResponse
from rest_framework.views import APIView # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.models import User,House,HouseMember  # Import model User từ api
from .serializers import UserRegistrationSerializer
from django.contrib.auth import authenticate # type: ignore
from rest_framework import status  # type: ignore # Import status để sử dụng các mã trạng thái HTTP
import logging
class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        # Lấy dữ liệu từ request
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Tạo người dùng và lưu vào cơ sở dữ liệu
            serializer.save()
            return JsonResponse({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        else:
            # Nếu có lỗi trong quá trình đăng ký, trả về lỗi
            return JsonResponse({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Cho phép tất cả người dùng truy cập vào view này

    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(
                type=openapi.TYPE_STRING, description="Username"
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING, description="Password"
            ),
        },
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(type=openapi.TYPE_NUMBER),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(type=openapi.TYPE_NUMBER),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    },
)
    def post(self, request):
        # print("hello")
        # logging.debug(f"Attempting to authenticate user: {request.data.get('username')}")
        username = request.data.get("username")
        password = request.data.get("password")
        # print(f"Attempting to authenticate user: {username}")
        user = authenticate(username=username, password=password)
        # print("hello", user)
        if user:
            # Tạo refresh token và access token
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        try:
            # Hủy refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return JsonResponse({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return JsonResponse({"message": "Invalid refresh token", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        #lấy house_id của người đó
        admin_house = House.objects.filter(admin=user).values_list('house_id', flat=True)
        member_house = HouseMember.objects.filter(user=user).values_list('house_id', flat=True)
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "address": user.address,
            "ssn": user.ssn,
            "role": user.role,
            "admin_house": list(admin_house),
            "member_house": list(member_house),
        })