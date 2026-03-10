from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),

    # LOGIN SYSTEM
    path('accounts/', include('accounts.urls')),

    # API
    path('api/accounts/', include('accounts.urls')),
    path('api/invoices/', include('invoices.urls')),
    path('api/checks/', include('checks.urls')),
    path('api/current-accounts/', include('current_accounts.urls')),
    path('api/personnel/', include('personnel.urls')),

]

admin.site.site_header = "ZENITHAR Yönetim Paneli"
admin.site.site_title = "ZENITHAR Admin"
admin.site.index_title = "Yönetim Paneli"