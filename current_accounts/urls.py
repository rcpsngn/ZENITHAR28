from django.urls import path
from . import views

urlpatterns = [
    path('stok-takip/', views.stok_takip, name='stok_takip'),
    path('cari-ekstre/', views.cari_ekstre, name='cari_ekstre'),
    path('cari-bakiye/', views.cari_bakiye, name='cari_bakiye'),
    path('alinan-faturalar/', views.alinan_faturalar, name='alinan_faturalar'),
    path('giden-faturalar/', views.giden_faturalar, name='giden_faturalar'),
]