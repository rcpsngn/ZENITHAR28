from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation

from .models import BankTransaction, CashTransaction, POSTransaction, Check, Promissory


def to_decimal(value, default="0"):
    if value is None or value == "":
        value = default
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal(default)


# ---- BANKA HAREKETLERİ ----

@login_required
def bank_transactions(request):
    transactions = BankTransaction.objects.filter(user=request.user)
    total_in = sum((t.amount for t in transactions if t.type == "deposit"), Decimal("0"))
    total_out = sum((t.amount for t in transactions if t.type == "withdrawal"), Decimal("0"))
    return render(request, 'checks/bank-transactions.html', {
        'transactions': transactions, 'total_in': total_in, 'total_out': total_out,
        'net_balance': total_in - total_out,
    })


@login_required
def bank_transaction_save(request):
    if request.method == "POST":
        BankTransaction.objects.create(
            user=request.user,
            bank_name=request.POST.get("bank_name"),
            account_number=request.POST.get("account_number", ""),
            type=request.POST.get("type", "deposit"),
            amount=to_decimal(request.POST.get("amount"), "0"),
            date=request.POST.get("date"),
            description=request.POST.get("description", ""),
        )
    return redirect("bank_transactions")


@login_required
def bank_transaction_delete(request, id):
    get_object_or_404(BankTransaction, id=id, user=request.user).delete()
    return redirect("bank_transactions")


# ---- KASA İŞLEMLERİ ----

@login_required
def cash_operations(request):
    transactions = CashTransaction.objects.filter(user=request.user)
    total_in = sum((t.amount for t in transactions if t.type == "in"), Decimal("0"))
    total_out = sum((t.amount for t in transactions if t.type == "out"), Decimal("0"))
    return render(request, 'checks/cash-operations.html', {
        'transactions': transactions, 'total_in': total_in, 'total_out': total_out,
        'cash_balance': total_in - total_out,
    })


@login_required
def cash_transaction_save(request):
    if request.method == "POST":
        CashTransaction.objects.create(
            user=request.user,
            type=request.POST.get("type", "in"),
            amount=to_decimal(request.POST.get("amount"), "0"),
            date=request.POST.get("date"),
            description=request.POST.get("description", ""),
        )
    return redirect("cash_operations")


@login_required
def cash_transaction_delete(request, id):
    get_object_or_404(CashTransaction, id=id, user=request.user).delete()
    return redirect("cash_operations")


# ---- POS & KREDİ KARTI ----

@login_required
def pos_credit_card(request):
    transactions = POSTransaction.objects.filter(user=request.user)
    total_gross = sum((t.amount for t in transactions), Decimal("0"))
    total_commission = sum((t.commission_amount for t in transactions), Decimal("0"))
    return render(request, 'checks/pos-credit-card.html', {
        'transactions': transactions, 'total_gross': total_gross,
        'total_commission': total_commission, 'total_net': total_gross - total_commission,
    })


@login_required
def pos_transaction_save(request):
    if request.method == "POST":
        POSTransaction.objects.create(
            user=request.user,
            card_type=request.POST.get("card_type", "credit"),
            amount=to_decimal(request.POST.get("amount"), "0"),
            commission_rate=to_decimal(request.POST.get("commission_rate"), "0"),
            date=request.POST.get("date"),
            description=request.POST.get("description", ""),
        )
    return redirect("pos_credit_card")


@login_required
def pos_transaction_delete(request, id):
    get_object_or_404(POSTransaction, id=id, user=request.user).delete()
    return redirect("pos_credit_card")


# ---- ÇEK / SENET TAKİP ----

@login_required
def checks_notes_tracking(request):
    checks = Check.objects.filter(user=request.user)
    promissories = Promissory.objects.filter(user=request.user)
    portfolio_total = sum((c.amount for c in checks if c.status == "portfolio"), Decimal("0")) + \
                      sum((p.amount for p in promissories if p.status == "portfolio"), Decimal("0"))
    return render(request, 'checks/checks-notes-tracking.html', {
        'checks': checks, 'promissories': promissories, 'portfolio_total': portfolio_total,
    })


@login_required
def check_save(request):
    if request.method == "POST":
        Check.objects.create(
            user=request.user,
            type=request.POST.get("type", "received"),
            check_number=request.POST.get("check_number"),
            bank_name=request.POST.get("bank_name"),
            branch=request.POST.get("branch", ""),
            account_number=request.POST.get("account_number", ""),
            payer_name=request.POST.get("payer_name"),
            amount=to_decimal(request.POST.get("amount"), "0"),
            issue_date=request.POST.get("issue_date"),
            due_date=request.POST.get("due_date"),
        )
    return redirect("checks_notes_tracking")


@login_required
def check_update_status(request, id, new_status):
    check = get_object_or_404(Check, id=id, user=request.user)
    check.status = new_status
    check.save(update_fields=["status"])
    return redirect("checks_notes_tracking")


@login_required
def check_delete(request, id):
    get_object_or_404(Check, id=id, user=request.user).delete()
    return redirect("checks_notes_tracking")


@login_required
def promissory_save(request):
    if request.method == "POST":
        Promissory.objects.create(
            user=request.user,
            type=request.POST.get("type", "received"),
            promissory_number=request.POST.get("promissory_number"),
            drawer_name=request.POST.get("drawer_name"),
            endorser_name=request.POST.get("endorser_name", ""),
            amount=to_decimal(request.POST.get("amount"), "0"),
            issue_date=request.POST.get("issue_date"),
            due_date=request.POST.get("due_date"),
            place_of_issue=request.POST.get("place_of_issue", ""),
        )
    return redirect("checks_notes_tracking")


@login_required
def promissory_update_status(request, id, new_status):
    promissory = get_object_or_404(Promissory, id=id, user=request.user)
    promissory.status = new_status
    promissory.save(update_fields=["status"])
    return redirect("checks_notes_tracking")


@login_required
def promissory_delete(request, id):
    get_object_or_404(Promissory, id=id, user=request.user).delete()
    return redirect("checks_notes_tracking")
