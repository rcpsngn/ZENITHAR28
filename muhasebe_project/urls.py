from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render


def home(request):
    return render(request, "index.html")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('api/accounts/', include('accounts.urls')),
    path('api/invoices/', include('invoices.urls')),
    path('api/checks/', include('checks.urls')),
    path('api/current-accounts/', include('current_accounts.urls')),
    path('api/personnel/', include('personnel.urls')),
]

admin.site.site_header = 'ZENITHAR Yönetim Paneli'
admin.site.site_title = 'ZENITHAR Admin'
admin.site.index_title = 'Yönetim Paneli'