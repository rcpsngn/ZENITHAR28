from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def bank_transactions(request):
    return render(request, 'checks/bank-transactions.html')

@login_required
def cash_operations(request):
    return render(request, 'checks/cash-operations.html')

@login_required
def pos_credit_card(request):
    return render(request, 'checks/pos-credit-card.html')

@login_required
def checks_notes_tracking(request):
    return render(request, 'checks/checks-notes-tracking.html')