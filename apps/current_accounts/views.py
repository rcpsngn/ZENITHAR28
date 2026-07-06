from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def stock_tracking(request):
    return render(request, 'current_accounts/stock-tracking.html')

@login_required
def account_statement(request):
    return render(request, 'current_accounts/account-statement.html')

@login_required
def current_balance(request):
    return render(request, 'current_accounts/current-balance.html')

@login_required
def received_invoices(request):
    return render(request, 'current_accounts/received-invoices.html')

@login_required
def sent_invoices(request):
    return render(request, 'current_accounts/sent-invoices.html')