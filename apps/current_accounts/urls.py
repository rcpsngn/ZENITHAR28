from django.urls import path
from . import views

urlpatterns = [
    path('stok-takip/', views.stock_tracking, name='stock_tracking'),
    path('cari-ekstre/', views.account_statement, name='account_statement'),
    path('cari-bakiye/', views.current_balance, name='current_balance'),
    path('alinan-faturalar/', views.received_invoices, name='received_invoices'),
    path('giden-faturalar/', views.sent_invoices, name='sent_invoices'),
]