from django.urls import path
from . import views

urlpatterns = [
    path('company-info/', views.company_info, name="company_info"),
    path('definitions/', views.definitions, name="definitions"),
    path('accountant/', views.accountant, name="accountant"),
    path('document-design/', views.document_design, name="document_design"),
    path('document-design/numbering/', views.document_numbering_settings, name="document_numbering_settings"),
    path('document-design/customize/', views.document_design_customize, name="document_design_customize_new"),
    path('document-design/customize/<uuid:id>/', views.document_design_customize, name="document_design_customize"),
    path('document-design/upload/', views.document_design_upload, name="document_design_upload"),
    path('document-design/preview/<uuid:id>/', views.document_design_preview, name="document_design_preview"),
    path('document-design/delete/<uuid:id>/', views.document_design_delete, name="document_design_delete"),
    path('document-design/set-default/<uuid:id>/', views.document_design_set_default, name="document_design_set_default"),
    path('document-design/toggle-active/<uuid:id>/', views.document_design_toggle_active, name="document_design_toggle_active"),
    path('document-design/download/<uuid:id>/', views.document_design_download, name="document_design_download"),
    path('portal/', views.portal_settings, name="portal_settings"),
    path('notifications/', views.notification_settings, name="notification_settings"),
    path('system/', views.system_settings, name="system_settings"),
    path('system/backup/', views.system_backup_download, name="system_backup_download"),
]