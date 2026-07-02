from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def stok_takip(request):
    return render(request, 'current_accounts/stock-tracking.html')

@login_required
def cari_ekstre(request):
    return render(request, 'current_accounts/account-statement.html')

@login_required
def cari_bakiye(request):
    return render(request, 'current_accounts/current-balance.html')

@login_required
def alinan_faturalar(request):
    return render(request, 'current_accounts/received-invoices.html')

@login_required
def giden_faturalar(request):
    return render(request, 'current_accounts/sent-invoices.html')