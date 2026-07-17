from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Subscription

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login atarken access/refresh token ile birlikte kullanıcı bilgisini de döner."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'company_name', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'company_name', 'phone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        Subscription.objects.create(user=user, plan='trial')
        return user

class SubscriptionSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'status', 'start_date', 'end_date', 'auto_renew', 'is_active']
    
    def get_is_active(self, obj):
        return obj.is_active()
