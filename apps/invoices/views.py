from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Invoice, InvoiceItem
from . import integrations
import uuid
import json
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import urllib.request
import xml.etree.ElementTree as ET


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


# API: TCMB CANLI DÖVİZ KURU ÇEKİCİ (GELİŞMİŞ SÜRÜM)
@login_required
def get_tcmb_rate(request):
    """
    TCMB'den canlı döviz kurlarını çeker.
    Eğer bugün resmi tatil veya hafta sonu ise, geriye doğru son yayınlanan iş gününü bulur.
    Seçenekler: forex_buying (Döviz Alış), forex_selling (Döviz Satış),
              eff_buying (Efektif Alış), eff_selling (Efektif Satış)
    """
    currency_code = request.GET.get("code", "USD").upper()
    rate_type = request.GET.get("type", "forex_buying") # Varsayılan olarak Döviz Alış

    # Eğer Türk Lirası seçildiyse doğrudan 1.0000 döndür
    if currency_code in ["TL", "TRY"]:
        return JsonResponse({"rate": "1.0000", "success": True})

    target_date = datetime.now()
    xml_data = None

    # Hafta sonu ve resmi tatilleri atlamak için geriye doğru 10 günlük güvenli tarama
    for _ in range(10):
        # TCMB URL yapısı: Bugün için doğrudan kurlar.xml, geçmiş günler için YYYYMM/DDMMYYYY.xml
        if target_date.date() == datetime.now().date():
            url = "https://www.tcmb.gov.tr/kurlar/kurlar.xml"
        else:
            date_str = target_date.strftime("%d%m%Y")
            folder_str = target_date.strftime("%Y%m")
            url = f"https://www.tcmb.gov.tr/kurlar/{folder_str}/{date_str}.xml"

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    xml_data = response.read()
                    break
        except Exception:
            # Hata alındıysa (Örn: 404 Not Found yani tatil günü), bir önceki güne geçip taramaya devam et
            target_date -= timedelta(days=1)
            continue

    if not xml_data:
        return JsonResponse({"error": "TCMB kurlarına şu an ulaşılamıyor.", "success": False}, status=400)

    try:
        root = ET.fromstring(xml_data)
        for currency in root.findall('Currency'):
            if currency.get('CurrencyCode') == currency_code:
                # Tüm kur varyasyonlarını XML içerisinden güvenli bir şekilde ayıklıyoruz
                forex_buying = currency.find('ForexBuying').text or "1.0000"
                forex_selling = currency.find('ForexSelling').text or "1.0000"
                banknote_buying = currency.find('BanknoteBuying').text or forex_buying
                banknote_selling = currency.find('BanknoteSelling').text or forex_selling

                # Eşleştirme haritası
                rates_map = {
                    "forex_buying": forex_buying.strip(),   # Döviz Alış
                    "forex_selling": forex_selling.strip(), # Döviz Satış
                    "eff_buying": banknote_buying.strip(),  # Efektif Alış
                    "eff_selling": banknote_selling.strip() # Efektif Satış
                }

                # İstenen kur tipini seç, eğer listede yoksa varsayılana (Döviz Alış) dön
                selected_rate = rates_map.get(rate_type, forex_buying)

                return JsonResponse({
                    "success": True,
                    "rate": selected_rate,
                    "currency": currency_code,
                    "date": target_date.strftime("%Y-%m-%d")
                })

        return JsonResponse({"error": f"{currency_code} kodu bültende bulunamadı.", "success": False}, status=404)

    except Exception as e:
        return JsonResponse({"error": f"Kur işlenirken hata oluştu: {str(e)}", "success": False}, status=500)


# API: GİB VERGİ DAİRESİ OTOMATİK SORGULAMA
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
            invoice_number=request.POST.get("invoice_number") or auto_invoice_number,
            type=request.POST.get("type", "e-fatura"),
            invoice_type=request.POST.get("invoice_type", "temel"),
            invoice_category=request.POST.get("invoice_category", "satis"),
            invoice_template=request.POST.get("invoice_template", "varsayilan"),
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
            customer_phone=request.POST.get("customer_phone", ""),
            customer_email=request.POST.get("customer_email", ""),
            customer_website=request.POST.get("customer_website", ""),
            delivery_country=request.POST.get("delivery_country", "Türkiye"),
            delivery_district=request.POST.get("delivery_district", ""),
            delivery_postal_code=request.POST.get("delivery_postal_code", ""),
            delivery_street=request.POST.get("delivery_street", ""),
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


# FATURA DÜZENLEME
@login_required
def invoice_edit(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user, status="draft")

    if request.method == "POST":
        invoice.invoice_type = request.POST.get("invoice_type", invoice.invoice_type)
        invoice.invoice_category = request.POST.get("invoice_category", invoice.invoice_category)
        invoice.invoice_template = request.POST.get("invoice_template", invoice.invoice_template)
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
        invoice.customer_phone = request.POST.get("customer_phone", "")
        invoice.customer_email = request.POST.get("customer_email", "")
        invoice.customer_website = request.POST.get("customer_website", "")
        invoice.delivery_country = request.POST.get("delivery_country", "Türkiye")
        invoice.delivery_district = request.POST.get("delivery_district", "")
        invoice.delivery_postal_code = request.POST.get("delivery_postal_code", "")
        invoice.delivery_street = request.POST.get("delivery_street", "")
        invoice.notes = request.POST.get("notes", "")
        invoice.save()

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
            "type": invoice.type,
            "ettn": invoice.ettn,
            "custom_no": invoice.custom_no,
            "invoice_number": invoice.invoice_number,
            "invoice_category": invoice.get_invoice_category_display(),
            "invoice_type": invoice.get_invoice_type_display(),
            "issue_date": str(invoice.issue_date),
            "currency": invoice.currency,
            "exchange_rate": str(invoice.exchange_rate),
            "customer_name": invoice.customer_name,
            "customer_tax_id": invoice.customer_tax_id,
            "customer_tax_office": invoice.customer_tax_office,
            "customer_street": invoice.customer_street,
            "customer_district": invoice.customer_district,
            "customer_city": invoice.customer_city,
            "customer_country": invoice.customer_country,
            "customer_postal_code": invoice.customer_postal_code,
            "customer_phone": invoice.customer_phone,
            "customer_email": invoice.customer_email,
            "customer_website": invoice.customer_website,
            "delivery_country": invoice.delivery_country,
            "delivery_district": invoice.delivery_district,
            "delivery_postal_code": invoice.delivery_postal_code,
            "delivery_street": invoice.delivery_street,
            "notes": invoice.notes,
            "amount": float(invoice.amount),
            "vat_amount": float(invoice.vat_amount),
            "total_amount": float(invoice.total_amount),
            "items": items_data
        })

    return render(request, "invoices/invoice-view.html", {"invoice": invoice})


@login_required
def invoices_draft(request):
    invoices = Invoice.objects.filter(user=request.user, status="draft", is_archived=False)
    return render(request, "invoices/invoices-draft.html", {"invoices": invoices, "active_tab": "draft"})


@login_required
def invoices_sent(request):
    invoices = Invoice.objects.filter(user=request.user, status="sent", is_archived=False)
    return render(request, "invoices/invoices-sent.html", {"invoices": invoices, "active_tab": "sent"})


@login_required
def invoice_send(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)
    integrations.send_efatura(invoice)
    invoice.status = "sent"
    invoice.save()
    return redirect("invoices_sent")


@login_required
def invoice_delete(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user, status="draft")
    invoice.delete()
    return redirect("invoices_draft")


def generate_invoice_number(prefix_code="ZNT"):
    current_year = datetime.now().year
    prefix = f"{prefix_code}{current_year}"
    last_invoice = Invoice.objects.filter(invoice_number__startswith=prefix).order_by('-invoice_number').first()
    if last_invoice:
        try:
            new_sequence = int(last_invoice.invoice_number[len(prefix):]) + 1
        except ValueError:
            new_sequence = 1
    else:
        new_sequence = 1
    return f"{prefix}{str(new_sequence).zfill(9)}"


@login_required
def invoice_cancel(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user, status="sent")
    invoice.status = "cancelled"
    invoice.save()
    return redirect("invoices_sent")


@login_required
def invoice_duplicate(request, id):
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
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        Invoice.objects.filter(id__in=ids, user=request.user, status="draft").delete()
    return redirect("invoices_draft")


@login_required
def invoices_incoming(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-fatura", is_archived=False).exclude(status="draft")
    unread_count = invoices.filter(is_read=False).count()
    return render(request, "invoices/invoices-incoming.html", {
        "invoices": invoices, "active_tab": "incoming", "unread_count": unread_count,
    })


@login_required
def earchive_incoming(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-arsiv", is_archived=False).exclude(status="draft")
    unread_count_earchive = invoices.filter(is_read=False).count()
    return render(request, "invoices/invoices-earchive-incoming.html", {
        "invoices": invoices, "active_tab": "earchive_incoming", "unread_count_earchive": unread_count_earchive,
    })


@login_required
def earchive_sent(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-arsiv", status="sent", is_archived=False)
    return render(request, "invoices/invoices-earchive-sent.html", {
        "invoices": invoices, "active_tab": "earchive_sent",
    })


def _safe_redirect(request, fallback):
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer) if referer else redirect(fallback)


@login_required
def invoice_toggle_read(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)
    invoice.is_read = not invoice.is_read
    invoice.save(update_fields=["is_read"])
    return _safe_redirect(request, "invoices_incoming")


@login_required
def invoice_toggle_archive(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)
    invoice.is_archived = not invoice.is_archived
    invoice.save(update_fields=["is_archived"])
    return _safe_redirect(request, "invoices_incoming")


@login_required
def invoice_approve(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)
    invoice.status = "approved"
    invoice.save(update_fields=["status"])
    return _safe_redirect(request, "invoices_incoming")


@login_required
def invoice_reject(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)
    invoice.status = "rejected"
    invoice.save(update_fields=["status"])
    return _safe_redirect(request, "invoices_incoming")


@login_required
def invoices_bulk_mark_read(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        Invoice.objects.filter(id__in=ids, user=request.user).update(is_read=True)
    return _safe_redirect(request, "invoices_incoming")


@login_required
def invoices_bulk_mark_unread(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        Invoice.objects.filter(id__in=ids, user=request.user).update(is_read=False)
    return _safe_redirect(request, "invoices_incoming")