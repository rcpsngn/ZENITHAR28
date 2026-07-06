from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'type', 'customer_name', 'total_amount', 'status', 'issue_date']
    list_filter = ['type', 'status', 'issue_date']
    search_fields = ['invoice_number', 'customer_name', 'customer_tax_id']
    inlines = [InvoiceItemInline]
    readonly_fields = ['created_at', 'updated_at']
