from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views  # Artık logout_view da views içinden gelecek

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),  # views.logout_view olarak güncellendi
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html"
        ),
        name="password_reset",
    ),

    # ==========================================
    # JWT / REST API UÇLARI (mobil uygulama, dış entegrasyon vb. için)
    # ==========================================
    path("api/register/", views.RegisterView.as_view(), name="api_register"),
    path("api/token/", views.CustomTokenObtainPairView.as_view(), name="api_token_obtain"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="api_token_verify"),
    path("api/logout/", views.LogoutAPIView.as_view(), name="api_logout"),
    path("api/profile/", views.ProfileView.as_view(), name="api_profile"),
    path("api/subscription/", views.SubscriptionView.as_view(), name="api_subscription"),
]