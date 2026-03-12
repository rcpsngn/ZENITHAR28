from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


urlpatterns = [

    path('', home, name="home"),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('eirsaliye/', include('eirsaliye.urls')),
    path('invoices/', include('invoices.urls')),
    path('checks/', include('checks.urls')),
    path('current-accounts/', include('current_accounts.urls')),
    path('personnel/', include('personnel.urls')),
]

admin.site.site_header = "ZENITHAR Yönetim Paneli"
admin.site.site_title = "ZENITHAR Admin"
admin.site.index_title = "Yönetim Paneli"
