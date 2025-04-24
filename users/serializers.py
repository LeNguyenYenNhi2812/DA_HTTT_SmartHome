# users/serializers.py

from rest_framework import serializers # type: ignore
from api.models import User  # Import User từ api

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name','username', 'password', 'email', 'ssn', 'phone', 'address', 'date_of_birth', 'role']

    def create(self, validated_data):
        # Tạo người dùng với mật khẩu đã được mã hóa
        user = User.objects.create_user(**validated_data)
        return user
