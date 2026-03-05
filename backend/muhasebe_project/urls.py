from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

admin.site.site_header = 'Muhasebe Yönetim Paneli'
admin.site.site_title = 'Muhasebe Admin'
admin.site.index_title = 'Yönetim Paneli'
