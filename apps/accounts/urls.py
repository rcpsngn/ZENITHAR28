from django.urls import path
from django.contrib.auth import views as auth_views
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
]