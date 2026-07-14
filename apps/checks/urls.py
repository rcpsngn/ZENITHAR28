from django.urls import path
from . import views

urlpatterns = [
    path('banka-hareketleri/', views.bank_transactions, name='bank_transactions'),
    path('banka-hareketleri/kaydet/', views.bank_transaction_save, name='bank_transaction_save'),
    path('banka-hareketleri/sil/<int:id>/', views.bank_transaction_delete, name='bank_transaction_delete'),

    path('kasa-islemleri/', views.cash_operations, name='cash_operations'),
    path('kasa-islemleri/kaydet/', views.cash_transaction_save, name='cash_transaction_save'),
    path('kasa-islemleri/sil/<int:id>/', views.cash_transaction_delete, name='cash_transaction_delete'),

    path('pos-kredi-karti/', views.pos_credit_card, name='pos_credit_card'),
    path('pos-kredi-karti/kaydet/', views.pos_transaction_save, name='pos_transaction_save'),
    path('pos-kredi-karti/sil/<int:id>/', views.pos_transaction_delete, name='pos_transaction_delete'),

    path('cek-senet-takip/', views.checks_notes_tracking, name='checks_notes_tracking'),
    path('cek-senet-takip/cek-kaydet/', views.check_save, name='check_save'),
    path('cek-senet-takip/cek-durum/<int:id>/<str:new_status>/', views.check_update_status, name='check_update_status'),
    path('cek-senet-takip/cek-sil/<int:id>/', views.check_delete, name='check_delete'),
    path('cek-senet-takip/senet-kaydet/', views.promissory_save, name='promissory_save'),
    path('cek-senet-takip/senet-durum/<int:id>/<str:new_status>/', views.promissory_update_status, name='promissory_update_status'),
    path('cek-senet-takip/senet-sil/<int:id>/', views.promissory_delete, name='promissory_delete'),
]
