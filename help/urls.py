from django.urls import path
from . import views

urlpatterns = [
    path('videos/', views.help_videos, name="help_videos"),
    path('tips/', views.usage_tips, name="usage_tips"),
]