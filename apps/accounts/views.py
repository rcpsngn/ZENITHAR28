from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .serializers import UserSerializer, RegisterSerializer, SubscriptionSerializer, CustomTokenObtainPairSerializer
from .models import Subscription


# JWT LOGIN (API) - /accounts/api/token/
class CustomTokenObtainPairView(TokenObtainPairView):
    """POST {username, password} -> {access, refresh, user}"""
    serializer_class = CustomTokenObtainPairSerializer


# JWT LOGOUT (API) - /accounts/api/logout/
class LogoutAPIView(APIView):
    """POST {refresh} -> refresh token'ı kara listeye alır, artık kullanılamaz."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Geçersiz veya süresi dolmuş token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Çıkış yapıldı, token kara listeye alındı."}, status=status.HTTP_205_RESET_CONTENT)



# REGISTER API
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


# LOGIN PAGE
def login_view(request):
    # Eğer kullanıcı zaten giriş yapmışsa, tekrar login sayfasını görmesin, direkt home'a gitsin
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Başarılı girişte home sayfasına (home.html) gider
        else:
            return render(request, "login.html", {
                "error": "Kullanıcı adı veya şifre hatalı"
            })

    return render(request, "login.html")


# REGISTER PAGE
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Bu kullanıcı adı zaten kullanılıyor"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("home")  # Kayıt sonrası home sayfasına yönlendirir

    return render(request, "register.html")


# DASHBOARD
@login_required(login_url='login')
def dashboard(request):
    return render(request, "index.html")


# LOGOUT ACTION
def logout_view(request):
    logout(request)
    return redirect("login")


# PROFILE API
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# SUBSCRIPTION API
class SubscriptionView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        subscription, created = Subscription.objects.get_or_create(
            user=self.request.user,
            defaults={"plan": "trial"}
        )
        return subscription