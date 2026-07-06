from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subscription, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ['username', 'email', 'role', 'company_name', 'is_active', 'created_at']

    list_filter = ['role', 'is_active', 'created_at']

    search_fields = ['username', 'email', 'company_name', 'phone']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Ek Bilgiler', {'fields': ('role', 'company_name', 'phone')}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'is_active']

    list_filter = ['plan', 'status', 'start_date']

    search_fields = ['user__username', 'user__email']

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = ['user', 'title', 'is_read', 'created_at']

    list_filter = ['is_read', 'created_at']

    search_fields = ['title', 'message', 'user__username']

    readonly_fields = ['created_at']