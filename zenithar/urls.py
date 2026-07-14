from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, timedelta
import json

# Accounts'tan login_view'u buraya dahil ediyoruz
from apps.accounts.views import login_view

@login_required
def home(request):
    # Arama kutusundan gelen kelimeyi yakalıyoruz
    query = request.GET.get('q', '').strip().lower()

    if query:
        if query == 'fatura':
            return redirect('invoices_create')
        elif query == 'cari':
            return redirect('current_balance')

    from apps.invoices.models import Invoice
    from apps.personnel.models import Employee
    from apps.checks.models import CashTransaction, BankTransaction

    user = request.user
    today = date.today()

    # ---- Üst kartlar (gerçek veri) ----
    active_employee_count = Employee.objects.filter(user=user, is_active=True).count()
    active_invoice_count = Invoice.objects.filter(user=user, type="e-fatura").exclude(status__in=["draft", "cancelled"]).count()

    year_start = today.replace(month=1, day=1)
    total_income = Invoice.objects.filter(
        user=user, type="e-fatura", status__in=["sent", "approved", "paid"], issue_date__gte=year_start
    ).aggregate(s=Sum("total_amount"))["s"] or 0

    cash_out = CashTransaction.objects.filter(user=user, type="out", date__gte=year_start).aggregate(s=Sum("amount"))["s"] or 0
    bank_out = BankTransaction.objects.filter(user=user, type="withdrawal", date__gte=year_start).aggregate(s=Sum("amount"))["s"] or 0
    total_expense = cash_out + bank_out

    # ---- Aylık gelir grafiği (son 6 ay) ----
    month_labels = []
    month_values = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        month_start = date(y, m, 1)
        month_end = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
        total = Invoice.objects.filter(
            user=user, type="e-fatura", status__in=["sent", "approved", "paid"],
            issue_date__gte=month_start, issue_date__lt=month_end
        ).aggregate(s=Sum("total_amount"))["s"] or 0
        month_labels.append(month_start.strftime("%b %Y"))
        month_values.append(float(total))

    # ---- Gider dağılımı (Kasa / Banka / POS Komisyonu) ----
    from apps.checks.models import POSTransaction
    pos_qs = POSTransaction.objects.filter(user=user, date__gte=year_start)
    pos_commission = sum((t.commission_amount for t in pos_qs), 0)

    expense_labels = ["Kasa Çıkışı", "Banka Çıkışı", "POS Komisyonu"]
    expense_values = [float(cash_out), float(bank_out), float(pos_commission)]

    return render(request, "home.html", {
        "active_employee_count": active_employee_count,
        "active_invoice_count": active_invoice_count,
        "total_income": total_income,
        "total_expense": total_expense,
        "month_labels_json": json.dumps(month_labels),
        "month_values_json": json.dumps(month_values),
        "expense_labels_json": json.dumps(expense_labels),
        "expense_values_json": json.dumps(expense_values),
    })


@login_required
def reports_view(request):
    from apps.invoices.models import Invoice
    from apps.current_accounts.models import CurrentAccount, Product
    from django.db.models import Count

    user = request.user
    today = date.today()
    year_start = today.replace(month=1, day=1)

    invoices_this_year = Invoice.objects.filter(user=user, type="e-fatura", issue_date__gte=year_start)
    status_summary_raw = invoices_this_year.values("status").annotate(count=Count("id"), total=Sum("total_amount")).order_by("-total")
    status_display_map = dict(Invoice.STATUS_CHOICES)
    status_summary = [
        {"status": status_display_map.get(row["status"], row["status"]), "count": row["count"], "total": row["total"]}
        for row in status_summary_raw
    ]

    top_customers = (
        invoices_this_year.exclude(status__in=["draft", "cancelled"])
        .values("customer_name")
        .annotate(total=Sum("total_amount"), count=Count("id"))
        .order_by("-total")[:5]
    )

    accounts = CurrentAccount.objects.filter(user=user)
    total_receivable = sum((a.balance for a in accounts if a.balance > 0), 0)
    total_payable = sum((-a.balance for a in accounts if a.balance < 0), 0)

    products = Product.objects.filter(user=user)
    total_stock_value = sum((p.stock_value for p in products), 0)
    low_stock_products = [p for p in products if p.is_low_stock]

    return render(request, "reports/general-reports.html", {
        "status_summary": status_summary,
        "top_customers": top_customers,
        "total_receivable": total_receivable,
        "total_payable": total_payable,
        "total_stock_value": total_stock_value,
        "low_stock_products": low_stock_products,
        "year": today.year,
    })


urlpatterns = [
    # 1. Tarayıcı açıldığında doğrudan login_view çalışır:
    path('', login_view, name="login_root"),

    # 2. Giriş yapıldıktan sonra ulaşılan ana sayfanız artık '/home/' adresindedir:
    path('home/', home, name="home"),

    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('waybill/', include('apps.waybill.urls')),
    path('invoices/', include('apps.invoices.urls')),
    path('checks/', include('apps.checks.urls')),
    path('current-accounts/', include('apps.current_accounts.urls')),
    path('personnel/', include('apps.personnel.urls')),
    path('reports/', reports_view, name="reports"),
    path('help/', include('apps.help.urls')),
    path('settings/', include('apps.settings_app.urls')),
]

admin.site.site_header = "ZENITHAR Yönetim Paneli"
admin.site.site_title = "ZENITHAR Admin"
admin.site.index_title = "Yönetim Paneli"