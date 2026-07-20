from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, timedelta
import json
from django.conf import settings
from django.conf.urls.static import static

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

    # ---- Belge hacmi trend grafiği (son 30 gün) — Uyumsoft portal referanslı ana sayfa ----
    from apps.help.models import Announcement

    trend_days = 30
    trend_start = today - timedelta(days=trend_days - 1)
    trend_labels = []
    efatura_series, earsiv_series, eirsaliye_series, pending_series = [], [], [], []

    # Tek seferde tüm aralığı çekip Python tarafında günlere dağıtmak, 30 gün
    # için 30*4 ayrı sorgu atmaktan çok daha verimli.
    docs_in_range = list(
        Invoice.objects.filter(user=user, issue_date__gte=trend_start, issue_date__lte=today)
        .exclude(status="draft")
        .values("issue_date", "type", "status")
    )

    for i in range(trend_days):
        day = trend_start + timedelta(days=i)
        trend_labels.append(day.strftime("%d %b"))
        day_docs = [d for d in docs_in_range if d["issue_date"] == day]
        efatura_series.append(sum(1 for d in day_docs if d["type"] == "e-fatura"))
        earsiv_series.append(sum(1 for d in day_docs if d["type"] == "e-arsiv"))
        eirsaliye_series.append(sum(1 for d in day_docs if d["type"] == "e-irsaliye"))
        pending_series.append(sum(1 for d in day_docs if d["status"] == "sent"))

    # ---- Genişletilmiş panel: durum bazlı özet kartlar (gerçek sayılar) ----
    all_docs_this_year = Invoice.objects.filter(user=user, issue_date__gte=year_start)
    status_counts = {
        "sent": all_docs_this_year.filter(status="sent").count(),
        "approved": all_docs_this_year.filter(status="approved").count(),
        "rejected": all_docs_this_year.filter(status="rejected").count(),
        "cancelled": all_docs_this_year.filter(status="cancelled").count(),
        "partially_accepted": all_docs_this_year.filter(status="partially_accepted").count(),
        "returned": all_docs_this_year.filter(status="returned").count(),
    }

    recent_incoming = Invoice.objects.filter(
        user=user, type="e-fatura", is_archived=False
    ).exclude(status="draft").order_by("-issue_date")[:5]

    recent_responses = Invoice.objects.filter(
        user=user, type="e-fatura", status__in=["approved", "rejected"],
    ).order_by("-issue_date")[:5]

    gib_announcements = Announcement.objects.filter(category="gib", is_active=True)[:5]
    general_announcements = Announcement.objects.filter(category="general", is_active=True)[:5]

    return render(request, "home.html", {
        "active_employee_count": active_employee_count,
        "active_invoice_count": active_invoice_count,
        "total_income": total_income,
        "total_expense": total_expense,

        "trend_labels_json": json.dumps(trend_labels),
        "trend_efatura_json": json.dumps(efatura_series),
        "trend_earsiv_json": json.dumps(earsiv_series),
        "trend_eirsaliye_json": json.dumps(eirsaliye_series),
        "trend_pending_json": json.dumps(pending_series),

        "status_counts": status_counts,
        "recent_incoming": recent_incoming,
        "recent_responses": recent_responses,
        "gib_announcements": gib_announcements,
        "general_announcements": general_announcements,
    })


@login_required
def reports_view(request):
    from apps.invoices.models import Invoice, InvoiceItem
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

    # Aşama 30 notu: "en çok satan ürün kırılımı eklenirse tamamlanabilir."
    # InvoiceItem'da Product'a bağlı bir foreign key olmadığı için (kalemler
    # serbest metin "description" ile tutuluyor), kırılım açıklama metnine
    # göre gruplanarak yapılıyor. Bu, gerçek bir Product FK'sinden daha az
    # kesin olsa da (ör. aynı ürün farklı yazılmışsa ayrı satır sayılır),
    # şema değişikliği gerektirmeden anlamlı bir yaklaşık sonuç verir.
    top_selling_products = (
        InvoiceItem.objects.filter(
            invoice__user=user, invoice__type="e-fatura", invoice__issue_date__gte=year_start,
        )
        .exclude(invoice__status__in=["draft", "cancelled"])
        .values("description")
        .annotate(total_quantity=Sum("quantity"), total_amount=Sum("total"))
        .order_by("-total_amount")[:5]
    )

    accounts = CurrentAccount.objects.filter(user=user)
    total_receivable = sum((a.balance for a in accounts if a.balance > 0), 0)
    total_payable = sum((-a.balance for a in accounts if a.balance < 0), 0)

    products = Product.objects.filter(user=user)
    total_stock_value = sum((p.stock_value for p in products), 0)
    low_stock_products = [p for p in products if p.is_low_stock]

    # Aşama 30 notu: "maliyet analizi ... eklenirse tamamlanabilir."
    # Product.cost_price (bu pakette eklendi) üzerinden potansiyel kâr hesabı.
    total_potential_profit = sum((p.potential_profit for p in products), 0)
    most_profitable_products = sorted(products, key=lambda p: p.potential_profit, reverse=True)[:5]

    return render(request, "reports/general-reports.html", {
        "status_summary": status_summary,
        "top_customers": top_customers,
        "top_selling_products": top_selling_products,
        "total_receivable": total_receivable,
        "total_payable": total_payable,
        "total_stock_value": total_stock_value,
        "low_stock_products": low_stock_products,
        "total_potential_profit": total_potential_profit,
        "most_profitable_products": most_profitable_products,
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

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "ZENITHAR Yönetim Paneli"
admin.site.site_title = "ZENITHAR Admin"
admin.site.index_title = "Yönetim Paneli"