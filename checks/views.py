from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def banka_hareketleri(request):
    return render(request, 'checks/banka-hareketleri.html')

@login_required
def kasa_islemleri(request):
    return render(request, 'checks/kasa-islemleri.html')

@login_required
def pos_kredi_karti(request):
    return render(request, 'checks/pos-kredi-karti.html')

@login_required
def cek_senet_takip(request):
    return render(request, 'checks/cek-senet-takip.html')