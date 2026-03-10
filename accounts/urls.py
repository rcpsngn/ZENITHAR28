from django.urls import path
from . import views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views


def logout_view(request):
    logout(request)
    return redirect("login")


urlpatterns = [

    path("login/", views.login_view, name="login"),

    path("register/", views.register_view, name="register"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("logout/", logout_view, name="logout"),

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html"
        ),
        name="password_reset",
    ),

]