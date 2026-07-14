from django.urls import path
from . import views

urlpatterns = [
    path('stok-takip/', views.stock_tracking, name='stock_tracking'),
    path('stok-takip/kaydet/', views.product_save, name='product_save'),
    path('stok-takip/kaydet/<int:id>/', views.product_save, name='product_edit'),
    path('stok-takip/sil/<int:id>/', views.product_delete, name='product_delete'),

    path('cari-bakiye/', views.current_balance, name='current_balance'),
    path('cari-bakiye/kaydet/', views.account_save, name='account_save'),
    path('cari-bakiye/kaydet/<int:id>/', views.account_save, name='account_edit'),
    path('cari-bakiye/sil/<int:id>/', views.account_delete, name='account_delete'),

    path('cari-ekstre/', views.account_statement, name='account_statement'),
    path('cari-ekstre/<int:id>/', views.account_statement, name='account_statement_detail'),
    path('cari-ekstre/<int:account_id>/islem-ekle/', views.transaction_save, name='transaction_save'),
    path('cari-ekstre/islem-sil/<int:id>/', views.transaction_delete, name='transaction_delete'),

    path('alinan-faturalar/', views.received_invoices, name='received_invoices'),
    path('giden-faturalar/', views.sent_invoices, name='sent_invoices'),
]
