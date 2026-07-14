from django.contrib import admin
from .models import Check, Promissory, BankTransaction, CashTransaction, POSTransaction

@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['bank_name', 'type', 'amount', 'date']
    list_filter = ['type', 'bank_name']

@admin.register(CashTransaction)
class CashTransactionAdmin(admin.ModelAdmin):
    list_display = ['type', 'amount', 'date', 'description']
    list_filter = ['type']

@admin.register(POSTransaction)
class POSTransactionAdmin(admin.ModelAdmin):
    list_display = ['card_type', 'amount', 'commission_rate', 'date']
    list_filter = ['card_type']

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
