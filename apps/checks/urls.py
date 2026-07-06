from django.urls import path
from . import views

urlpatterns = [
    path('banka-hareketleri/', views.bank_transactions, name='bank_transactions'),
    path('kasa-islemleri/', views.cash_operations, name='cash_operations'),
    path('pos-kredi-karti/', views.pos_credit_card, name='pos_credit_card'),
    path('cek-senet-takip/', views.checks_notes_tracking, name='checks_notes_tracking'),
]