from django.urls import path, include

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("personnel/", include("personnel.urls")),
    path("invoices/", include("invoices.urls")),
]