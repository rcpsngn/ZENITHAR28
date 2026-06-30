from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def stok_takip(request):
    return render(request, 'current_accounts/stok-takip.html')

@login_required
def cari_ekstre(request):
    return render(request, 'current_accounts/cari-ekstre.html')

@login_required
def cari_bakiye(request):
    return render(request, 'current_accounts/cari-bakiye.html')

@login_required
def alinan_faturalar(request):
    return render(request, 'current_accounts/alinan-faturalar.html')

@login_required
def giden_faturalar(request):
    return render(request, 'current_accounts/giden-faturalar.html')