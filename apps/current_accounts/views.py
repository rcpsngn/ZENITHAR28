from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal, InvalidOperation

from .models import CurrentAccount, Transaction, Product


def to_decimal(value, default="0"):
    """Formdan gelen sayı metnini güvenli şekilde Decimal'e çevirir (virgül/nokta farkına tolerant)."""
    if value is None or value == "":
        value = default
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal(default)


# ---- STOK TAKİP ----

@login_required
def stock_tracking(request):
    products = Product.objects.filter(user=request.user)
    total_stock_value = sum((p.stock_value for p in products), Decimal("0"))
    low_stock_count = sum(1 for p in products if p.is_low_stock)
    return render(request, 'current_accounts/stock-tracking.html', {
        'products': products,
        'total_stock_value': total_stock_value,
        'low_stock_count': low_stock_count,
    })


@login_required
def product_save(request, id=None):
    product = get_object_or_404(Product, id=id, user=request.user) if id else Product(user=request.user)
    if request.method == "POST":
        product.code = request.POST.get("code", "")
        product.name = request.POST.get("name")
        product.category = request.POST.get("category", "")
        product.unit = request.POST.get("unit", "Adet")
        product.quantity = to_decimal(request.POST.get("quantity"), "0")
        product.unit_price = to_decimal(request.POST.get("unit_price"), "0")
        product.vat_rate = to_decimal(request.POST.get("vat_rate"), "20")
        product.min_stock_level = to_decimal(request.POST.get("min_stock_level"), "0")
        product.save()
    return redirect("stock_tracking")


@login_required
def product_delete(request, id):
    get_object_or_404(Product, id=id, user=request.user).delete()
    return redirect("stock_tracking")


# ---- CARİ BAKİYE ----

@login_required
def current_balance(request):
    accounts = CurrentAccount.objects.filter(user=request.user)
    total_receivable = sum((a.balance for a in accounts if a.balance > 0), Decimal("0"))
    total_payable = sum((-a.balance for a in accounts if a.balance < 0), Decimal("0"))
    return render(request, 'current_accounts/current-balance.html', {
        'accounts': accounts,
        'total_receivable': total_receivable,
        'total_payable': total_payable,
    })


@login_required
def account_save(request, id=None):
    account = get_object_or_404(CurrentAccount, id=id, user=request.user) if id else CurrentAccount(user=request.user)
    if request.method == "POST":
        account.type = request.POST.get("type", "customer")
        account.name = request.POST.get("name")
        account.company_name = request.POST.get("company_name", "")
        account.tax_id = request.POST.get("tax_id", "")
        account.tax_office = request.POST.get("tax_office", "")
        account.email = request.POST.get("email", "")
        account.phone = request.POST.get("phone", "")
        account.address = request.POST.get("address", "")
        account.credit_limit = to_decimal(request.POST.get("credit_limit"), "0")
        account.notes = request.POST.get("notes", "")
        if not id:
            account.balance = to_decimal(request.POST.get("balance"), "0")
        account.save()
    return redirect("current_balance")


@login_required
def account_delete(request, id):
    get_object_or_404(CurrentAccount, id=id, user=request.user).delete()
    return redirect("current_balance")


# ---- CARİ EKSTRE ----

@login_required
def account_statement(request, id=None):
    accounts = CurrentAccount.objects.filter(user=request.user)
    selected_account = None
    transactions = []
    running_rows = []

    account_id = id or request.GET.get("account_id")
    if account_id:
        selected_account = get_object_or_404(CurrentAccount, id=account_id, user=request.user)
        transactions = selected_account.transactions.order_by("date", "id")
        balance = Decimal("0")
        for t in transactions:
            if t.type == "debit":
                balance += t.amount
            else:
                balance -= t.amount
            running_rows.append({"t": t, "running_balance": balance})

    return render(request, 'current_accounts/account-statement.html', {
        'accounts': accounts,
        'selected_account': selected_account,
        'running_rows': running_rows,
    })


@login_required
def transaction_save(request, account_id):
    account = get_object_or_404(CurrentAccount, id=account_id, user=request.user)
    if request.method == "POST":
        transaction = Transaction.objects.create(
            current_account=account,
            type=request.POST.get("type", "debit"),
            amount=to_decimal(request.POST.get("amount"), "0"),
            description=request.POST.get("description", ""),
            date=request.POST.get("date"),
            document_number=request.POST.get("document_number", ""),
        )
        if transaction.type == "debit":
            account.balance += transaction.amount
        else:
            account.balance -= transaction.amount
        account.save(update_fields=["balance"])
    return redirect(f"/current-accounts/cari-ekstre/{account_id}/")


@login_required
def transaction_delete(request, id):
    transaction = get_object_or_404(Transaction, id=id, current_account__user=request.user)
    account = transaction.current_account
    if transaction.type == "debit":
        account.balance -= transaction.amount
    else:
        account.balance += transaction.amount
    account.save(update_fields=["balance"])
    account_id = account.id
    transaction.delete()
    return redirect(f"/current-accounts/cari-ekstre/{account_id}/")


# ---- ALINAN / GİDEN E-FATURALAR ----
# Bu veriler zaten e-Fatura modülünde (Gelen/Giden E-Faturalar) tutuluyor.
# Tekrar aynı tabloyu burada oluşturmak yerine oraya yönlendiriyoruz;
# böylece tek bir doğru veri kaynağı (single source of truth) kalıyor.

@login_required
def received_invoices(request):
    return redirect("invoices_incoming")


@login_required
def sent_invoices(request):
    return redirect("invoices_sent")
