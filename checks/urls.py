from django.urls import path
from . import views

urlpatterns = [
    path('banka-hareketleri/', views.banka_hareketleri, name='banka_hareketleri'),
    path('kasa-islemleri/', views.kasa_islemleri, name='kasa_islemleri'),
    path('pos-kredi-karti/', views.pos_kredi_karti, name='pos_kredi_karti'),
    path('cek-senet-takip/', views.cek_senet_takip, name='cek_senet_takip'),
]