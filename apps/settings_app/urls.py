from django.urls import path
from . import views

urlpatterns = [
    path('company-info/', views.company_info, name="company_info"),
    path('definitions/', views.definitions, name="definitions"),
    path('accountant/', views.accountant, name="accountant"),
    path('document-design/', views.document_design, name="document_design"),
    path('portal/', views.portal_settings, name="portal_settings"),
    path('notifications/', views.notification_settings, name="notification_settings"),
    path('system/', views.system_settings, name="system_settings"),
    path('system/backup/', views.system_backup_download, name="system_backup_download"),
]