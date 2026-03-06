from django.contrib import admin
from .models import CurrentAccount, Transaction, VATOperation

@admin.register(CurrentAccount)
class CurrentAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'type', 'balance', 'is_active']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['name', 'company_name', 'tax_id', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['current_account', 'type', 'amount', 'date', 'description']
    list_filter = ['type', 'date']
    search_fields = ['current_account__name', 'description', 'document_number']

@admin.register(VATOperation)
class VATOperationAdmin(admin.ModelAdmin):
    list_display = ['type', 'period', 'amount', 'status', 'application_date']
    list_filter = ['type', 'status', 'application_date']
    search_fields = ['period', 'notes']
    readonly_fields = ['created_at', 'updated_at']
