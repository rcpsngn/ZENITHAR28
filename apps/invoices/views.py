from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Invoice, InvoiceItem
from . import integrations
import uuid
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation


def to_decimal(value, default="0"):
    """
    Formdan/JSON'dan gelen sayı metnini Decimal'e çevirir.
    Türkçe yerel ayar (LANGUAGE_CODE = 'tr-tr') sayıları bazen virgüllü
    (ör. '1,0000') gösterebildiği için, virgülü noktaya çevirerek
    dönüştürmeyi güvenli hale getirir.
    """
    if value is None or value == "":
        value = default
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def invoices_home(request):
    return redirect("invoices_draft")


# API: TCMB CANLI DÖVİZ KURU ÇEKİCİ
# Gerçek çağrı apps/invoices/integrations.py içinde toplanıyor.
def get_tcmb_rate(request):
    currency_code = request.GET.get("code", "TL")
    rate = integrations.get_exchange_rate(currency_code)
    return JsonResponse({"rate": rate})


# API: GİB VERGİ DAİRESİ OTOMATİK SORGULAMA
# Şu an simülasyon modunda çalışıyor. Gerçek entegrasyon için
# apps/invoices/integrations.py -> lookup_vkn() fonksiyonuna bak.
def vkn_sorgula(request):
    vkn = request.GET.get("vkn", "")
    result = integrations.lookup_vkn(vkn)
    return JsonResponse(result)


# FATURA OLUŞTURMA
@login_required
def invoices_page(request):
    if request.method == "POST":
        auto_ettn = str(uuid.uuid4())
        current_year = datetime.now().year
        prefix = f"ZNT{current_year}"

        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()

        if last_invoice:
            try:
                last_sequence = int(last_invoice.invoice_number[7:])
                new_sequence = last_sequence + 1
            except ValueError:
                new_sequence = 1
        else:
            new_sequence = 1

        auto_invoice_number = f"{prefix}{str(new_sequence).zfill(9)}"

        invoice = Invoice.objects.create(
            user=request.user, ettn=auto_ettn, custom_no="TR1.2",
            invoice_number=auto_invoice_number,
            type=request.POST.get("type", "e-fatura"),
            invoice_type=request.POST.get("invoice_type", "satis"),
            issue_date=request.POST.get("date") or datetime.now().date(),
            currency=request.POST.get("currency", "TL"),
            exchange_rate=to_decimal(request.POST.get("exchange_rate"), "1.0000"),
            customer_name=request.POST.get("customer_name"),
            customer_tax_id=request.POST.get("customer_tax_id", ""),
            customer_tax_office=request.POST.get("customer_tax_office", ""),
            customer_first_name=request.POST.get("customer_first_name", ""),
            customer_last_name=request.POST.get("customer_last_name", ""),
            customer_country=request.POST.get("customer_country", "Türkiye"),
            customer_city=request.POST.get("customer_city", ""),
            customer_district=request.POST.get("customer_district", ""),
            customer_street=request.POST.get("customer_street", ""),
            customer_postal_code=request.POST.get("customer_postal_code", ""),
            notes=request.POST.get("notes", ""), status="draft"
        )

        items_json = request.POST.get("items_json_data", "[]")
        try:
            items_list = json.loads(items_json)
            for item in items_list:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item.get("desc"),
                    quantity=to_decimal(item.get("qty"), "1"),
                    unit=item.get("unit"),
                    unit_price=to_decimal(item.get("price"), "0"),
                    vat_rate=to_decimal(item.get("vat"), "0")
                )
        except Exception:
            pass

        return redirect("invoices_draft")

    return render(request, "invoices/invoices-create.html")


# FATURA DÜZENLEME (sadece taslak durumundaki faturalar düzenlenebilir)
@login_required
def invoice_edit(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user, status="draft")

    if request.method == "POST":
        invoice.invoice_type = request.POST.get("invoice_type", invoice.invoice_type)
        invoice.issue_date = request.POST.get("date") or invoice.issue_date
        invoice.currency = request.POST.get("currency", invoice.currency)
        invoice.exchange_rate = to_decimal(request.POST.get("exchange_rate"), "1.0000")
        invoice.customer_name = request.POST.get("customer_name")
        invoice.customer_tax_id = request.POST.get("customer_tax_id", "")
        invoice.customer_tax_office = request.POST.get("customer_tax_office", "")
        invoice.customer_first_name = request.POST.get("customer_first_name", "")
        invoice.customer_last_name = request.POST.get("customer_last_name", "")
        invoice.customer_country = request.POST.get("customer_country", "Türkiye")
        invoice.customer_city = request.POST.get("customer_city", "")
        invoice.customer_district = request.POST.get("customer_district", "")
        invoice.customer_street = request.POST.get("customer_street", "")
        invoice.customer_postal_code = request.POST.get("customer_postal_code", "")
        invoice.notes = request.POST.get("notes", "")
        invoice.save()

        # Mevcut kalemleri silip, formdan gelen güncel kalem listesini yeniden oluştur.
        invoice.items.all().delete()
        items_json = request.POST.get("items_json_data", "[]")
        try:
            items_list = json.loads(items_json)
            for item in items_list:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item.get("desc"),
                    quantity=to_decimal(item.get("qty"), "1"),
                    unit=item.get("unit"),
                    unit_price=to_decimal(item.get("price"), "0"),
                    vat_rate=to_decimal(item.get("vat"), "0")
                )
        except Exception:
            pass

        return redirect("invoices_draft")

    items_json = json.dumps([
        {
            "desc": item.description,
            "qty": float(item.quantity),
            "unit": item.unit,
            "price": float(item.unit_price),
            "vat": float(item.vat_rate),
        }
        for item in invoice.items.all()
    ])

    return render(request, "invoices/invoices-create.html", {
        "invoice": invoice,
        "items_json": items_json,
    })


# DETAY GÖRÜNTÜLEME VE POPUP JSON ÖNİZLEME KÖPRÜSÜ
@login_required
def invoice_view(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)

    if request.GET.get("format") == "json":
        items_data = []
        for item in invoice.items.all():
            items_data.append({
                "desc": item.description,
                "qty": float(item.quantity),
                "unit": item.unit,
                "price": float(item.unit_price),
                "vat_rate": float(item.vat_rate),
                "vat_amount": float(item.vat_amount),
                "total": float(item.total)
            })

        return JsonResponse({
            "status": invoice.status,
            "ettn": invoice.ettn,
            "invoice_number": invoice.invoice_number,
            "issue_date": str(invoice.issue_date),
            "currency": invoice.currency,
            "exchange_rate": str(invoice.exchange_rate),
            "customer_name": invoice.customer_name,
            "customer_tax_id": invoice.customer_tax_id,
            "customer_tax_office": invoice.customer_tax_office,
            "customer_street": invoice.customer_street,
            "customer_district": invoice.customer_district,
            "customer_city": invoice.customer_city,
            "amount": float(invoice.amount),
            "vat_amount": float(invoice.vat_amount),
            "total_amount": float(invoice.total_amount),
            "items": items_data
        })

    return render(request, "invoices/invoice-view.html", {"invoice": invoice})


@login_required
def invoices_draft(request):
    invoices = Invoice.objects.filter(user=request.user, status="draft")
    return render(request, "invoices/invoices-draft.html", {"invoices": invoices})


@login_required
def invoices_sent(request):
    invoices = Invoice.objects.filter(user=request.user, status="sent")
    return render(request, "invoices/invoices-sent.html", {"invoices": invoices})


@login_required
def invoice_send(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)
    # Gerçek e-Fatura entegrasyonu eklendiğinde bu satır gerçek gönderimi
    # tetikleyecek. Şu an simülasyon: apps/invoices/integrations.py -> send_efatura()
    integrations.send_efatura(invoice)
    invoice.status = "sent"
    invoice.save()
    return redirect("invoices_sent")


@login_required
def invoice_delete(request, id):
    """Sadece TASLAK faturalar silinebilir. Gönderilmiş/resmi fatura asla silinmez, sadece iptal edilir (bkz. invoice_cancel)."""
    invoice = get_object_or_404(Invoice, id=id, user=request.user, status="draft")
    invoice.delete()
    return redirect("invoices_draft")


def generate_invoice_number():
    """create/duplicate akışlarında kullanılan otomatik fatura no üretici."""
    current_year = datetime.now().year
    prefix = f"ZNT{current_year}"
    last_invoice = Invoice.objects.filter(invoice_number__startswith=prefix).order_by('-invoice_number').first()
    if last_invoice:
        try:
            new_sequence = int(last_invoice.invoice_number[7:]) + 1
        except ValueError:
            new_sequence = 1
    else:
        new_sequence = 1
    return f"{prefix}{str(new_sequence).zfill(9)}"


@login_required
def invoice_cancel(request, id):
    """
    Resmi olarak kesilmiş (gönderilmiş) bir faturayı GERÇEK e-Fatura mantığına
    uygun şekilde İPTAL EDER. Silme değildir — kayıt yasal/denetim amacıyla
    veritabanında durumu 'cancelled' olarak kalır, listeden çıkar.
    """
    invoice = get_object_or_404(Invoice, id=id, user=request.user, status="sent")
    invoice.status = "cancelled"
    invoice.save()
    return redirect("invoices_sent")


@login_required
def invoice_duplicate(request, id):
    """Var olan bir faturanın (kalemleriyle birlikte) kopyasını yeni bir taslak olarak oluşturur."""
    original = get_object_or_404(Invoice, id=id, user=request.user)

    new_invoice = Invoice.objects.create(
        user=request.user,
        ettn=str(uuid.uuid4()),
        custom_no=original.custom_no,
        type=original.type,
        invoice_type=original.invoice_type,
        invoice_number=generate_invoice_number(),
        currency=original.currency,
        exchange_rate=original.exchange_rate,
        customer_name=original.customer_name,
        customer_first_name=original.customer_first_name,
        customer_last_name=original.customer_last_name,
        customer_tax_id=original.customer_tax_id,
        customer_tax_office=original.customer_tax_office,
        customer_country=original.customer_country,
        customer_city=original.customer_city,
        customer_district=original.customer_district,
        customer_street=original.customer_street,
        customer_postal_code=original.customer_postal_code,
        notes=original.notes,
        issue_date=datetime.now().date(),
        status="draft",
    )

    for item in original.items.all():
        InvoiceItem.objects.create(
            invoice=new_invoice,
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            vat_rate=item.vat_rate,
        )

    new_invoice.update_totals()
    return redirect("invoices_draft")


@login_required
def invoices_bulk_delete(request):
    """Taslaklar listesinde işaretlenen faturaları topluca siler. Güvenlik için sadece 'draft' durumundakiler silinir."""
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        Invoice.objects.filter(id__in=ids, user=request.user, status="draft").delete()
    return redirect("invoices_draft")


@login_required
def invoices_incoming(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-fatura")
    return render(request, "invoices/invoices-incoming.html", {"invoices": invoices})


@login_required
def earchive_incoming(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-arsiv", status="incoming")
    return render(request, "invoices/invoices-earchive-incoming.html", {"invoices": invoices})


@login_required
def earchive_sent(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-arsiv", status="sent")
    return render(request, "invoices/invoices-earchive-sent.html", {"invoices": invoices})