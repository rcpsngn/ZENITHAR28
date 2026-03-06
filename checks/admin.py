from django.contrib import admin
from .models import Check, Promissory

@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ['check_number', 'type', 'payer_name', 'amount', 'due_date', 'status']
    list_filter = ['type', 'status', 'due_date']
    search_fields = ['check_number', 'payer_name', 'bank_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Promissory)
class PromissoryAdmin(admin.ModelAdmin):
    list_display = ['promissory_number', 'type', 'drawer_name', 'amount', 'due_date', 'status']
    list_filter = ['type', 'status', 'due_date']
    search_fields = ['promissory_number', 'drawer_name', 'endorser_name']
    readonly_fields = ['created_at', 'updated_at']
