from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_date", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title", "summary")
