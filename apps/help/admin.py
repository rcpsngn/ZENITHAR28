from django.contrib import admin
from .models import Announcement, HelpVideo, UsageTip


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_date", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title", "summary")


@admin.register(HelpVideo)
class HelpVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(UsageTip)
class UsageTipAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
