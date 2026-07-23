from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Invoice, InvoiceItem
from . import integrations
from . import notifications
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


def _optional_item_kwargs(item: dict) -> dict:
    """
    Aşama 46/47/54: kalem JSON'undaki opsiyonel "Diğer Seçenekler" ve KDV
    muafiyet sebebi alanlarını InvoiceItem.objects.create() için kwarg
    sözlüğüne çevirir. Tüm alanlar isteğe bağlıdır; JS tarafında
    gönderilmezse boş string/None olarak düşer, ValidationError oluşmaz.

    Hem e-Fatura (apps/invoices/views.py) hem e-İrsaliye (apps/waybill/views.py)
    kalemleri aynı InvoiceItem modelini kullandığı için bu fonksiyon ortaktır.
    """
    def _date_or_none(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    return {
        "vat_exemption_reason": item.get("vat_exemption_reason", ""),
        "seller_code": item.get("seller_code", ""),
        "buyer_code": item.get("buyer_code", ""),
        "barcode": item.get("barcode", ""),
        "brand": item.get("brand", ""),
        "model_name": item.get("model_name", ""),
        "additional_description": item.get("additional_description", ""),
        "item_note": item.get("item_note", ""),
        "origin_country": item.get("origin_country", ""),
        "classification_value": item.get("classification_value", ""),
        "classification_version": item.get("classification_version", ""),
        "classification_code": item.get("classification_code", ""),
        "related_waybill_number": item.get("related_waybill_number", ""),
        "related_waybill_date": _date_or_none(item.get("related_waybill_date")),
        "order_number": item.get("order_number", ""),
        "order_date": _date_or_none(item.get("order_date")),
        "additional_info_id": item.get("additional_info_id", ""),
    }


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

        # Aşama 36: seri no öneki artık sabit "ZNT" değil, kullanıcının
        # Genel Ayarlar > Belge Tasarımı sayfasında kaydettiği değerden okunuyor.
        try:
            from apps.settings_app.models import DocumentDesignSettings
            design = DocumentDesignSettings.objects.filter(user=request.user).first()
            prefix_code = design.invoice_number_prefix if design else "ZNT"
        except Exception:
            prefix_code = "ZNT"

        prefix = f"{prefix_code}{current_year}"

        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()

        if last_invoice:
            try:
                last_sequence = int(last_invoice.invoice_number[len(prefix):])
                new_sequence = last_sequence + 1
            except ValueError:
                new_sequence = 1
        else:
            new_sequence = 1

        auto_invoice_number = f"{prefix}{str(new_sequence).zfill(9)}"

        # Aşama 56: fatura bir cari hesaba bağlanabilir. Formda doğrudan seçim
        # yapılmadıysa, müşteri VKN/TCKN'si mevcut bir cariyle eşleşiyorsa
        # otomatik olarak o cariye bağlanır (manuel iş yükünü azaltır).
        current_account = None
        current_account_id = request.POST.get("current_account")
        if current_account_id:
            from apps.current_accounts.models import CurrentAccount
            current_account = CurrentAccount.objects.filter(id=current_account_id, user=request.user).first()
        else:
            customer_tax_id = request.POST.get("customer_tax_id", "").strip()
            if customer_tax_id:
                from apps.current_accounts.models import CurrentAccount
                current_account = CurrentAccount.objects.filter(user=request.user, tax_id=customer_tax_id).first()

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
            current_account=current_account,
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
            notes=request.POST.get("notes", ""), status="draft",
            # Aşama 48/49: yalnızca invoice_type='ihracat' iken anlamlı, ama
            # her zaman kaydedilebilir (boşsa sorun olmaz, formda gösterilmez).
            export_gtip_no=request.POST.get("export_gtip_no", ""),
            export_delivery_terms=request.POST.get("export_delivery_terms", ""),
            export_shipping_method=request.POST.get("export_shipping_method", ""),
            export_package_marks=request.POST.get("export_package_marks", ""),
            export_package_number=request.POST.get("export_package_number", ""),
            export_package_count=request.POST.get("export_package_count", ""),
            export_customs_tracking_no=request.POST.get("export_customs_tracking_no", ""),
            export_delivery_country=request.POST.get("export_delivery_country", ""),
            export_delivery_city=request.POST.get("export_delivery_city", ""),
            export_delivery_district=request.POST.get("export_delivery_district", ""),
            export_delivery_town=request.POST.get("export_delivery_town", ""),
            export_delivery_street=request.POST.get("export_delivery_street", ""),
            export_delivery_postal_code=request.POST.get("export_delivery_postal_code", ""),
            export_delivery_building_name=request.POST.get("export_delivery_building_name", ""),
            export_delivery_building_no=request.POST.get("export_delivery_building_no", ""),
            export_delivery_door_no=request.POST.get("export_delivery_door_no", ""),
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
                    vat_rate=to_decimal(item.get("vat"), "0"),
                    **_optional_item_kwargs(item),
                )
        except Exception:
            pass

        return redirect("invoices_draft")

    # Aşama 44 devamı: Belge Tasarımları modülünden bu belge türü (e-Fatura)
    # için kaydedilmiş, aktif tasarımlar "Fatura Şablonu" alanına gerçek
    # seçenekler olarak sunulur.
    from apps.settings_app.models import DocumentTemplate
    document_templates = DocumentTemplate.objects.filter(
        user=request.user, document_type="e-fatura", is_active=True
    )
    return render(request, "invoices/invoices-create.html", {"document_templates": document_templates})


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
        invoice.export_gtip_no = request.POST.get("export_gtip_no", "")
        invoice.export_delivery_terms = request.POST.get("export_delivery_terms", "")
        invoice.export_shipping_method = request.POST.get("export_shipping_method", "")
        invoice.export_package_marks = request.POST.get("export_package_marks", "")
        invoice.export_package_number = request.POST.get("export_package_number", "")
        invoice.export_package_count = request.POST.get("export_package_count", "")
        invoice.export_customs_tracking_no = request.POST.get("export_customs_tracking_no", "")
        invoice.export_delivery_country = request.POST.get("export_delivery_country", "")
        invoice.export_delivery_city = request.POST.get("export_delivery_city", "")
        invoice.export_delivery_district = request.POST.get("export_delivery_district", "")
        invoice.export_delivery_town = request.POST.get("export_delivery_town", "")
        invoice.export_delivery_street = request.POST.get("export_delivery_street", "")
        invoice.export_delivery_postal_code = request.POST.get("export_delivery_postal_code", "")
        invoice.export_delivery_building_name = request.POST.get("export_delivery_building_name", "")
        invoice.export_delivery_building_no = request.POST.get("export_delivery_building_no", "")
        invoice.export_delivery_door_no = request.POST.get("export_delivery_door_no", "")
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
                    vat_rate=to_decimal(item.get("vat"), "0"),
                    **_optional_item_kwargs(item),
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

    from apps.settings_app.models import DocumentTemplate
    document_templates = DocumentTemplate.objects.filter(
        user=request.user, document_type="e-fatura", is_active=True
    )
    return render(request, "invoices/invoices-create.html", {
        "invoice": invoice,
        "items_json": items_json,
        "document_templates": document_templates,
    })


# DETAY GÖRÜNTÜLEME VE POPUP JSON ÖNİZLEME KÖPRÜSÜ
# DETAY GÖRÜNTÜLEME VE POPUP JSON ÖNİZLEME KÖPRÜSÜ
@login_required
def invoice_view(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)

    if request.GET.get("format") == "json":
        from apps.settings_app.models import CompanyProfile
        try:
            company = invoice.user.company_profile
            company_data = {
                "name": company.company_name,
                "address": company.address,
                "tax_id": company.tax_id,
                "tax_office": company.tax_office,
                "phone": company.phone,
                "email": company.email,
                "website": company.website,
                "logo_url": company.logo.url if company.logo else "",
            }
        except CompanyProfile.DoesNotExist:
            company_data = {
                "name": "Firmanızın Adı (Ayarlar > Firma Bilgileri'nden düzenleyin)",
                "address": "", "tax_id": "", "tax_office": "", "phone": "", "email": "", "website": "", "logo_url": "",
            }

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
            "company": company_data,
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
    result = integrations.send_invoice_to_gib(invoice, user=request.user)

    if result["success"]:
        invoice.status = "sent"
        if result.get("ettn"):
            invoice.ettn = result["ettn"]
        invoice.save()
        if result.get("simulated"):
            messages.info(request, f"{invoice.invoice_number}: {result['message']}")
        else:
            messages.success(request, f"{invoice.invoice_number}: {result['message']}")
    else:
        # Gönderim başarısız olduysa fatura DURUMU DEĞİŞTİRİLMEZ; taslak/mevcut
        # durumunda kalır, kullanıcı tekrar deneyebilir.
        messages.error(request, f"{invoice.invoice_number} GİB'e gönderilemedi: {result['message']}")

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
    result = integrations.cancel_invoice_at_gib(invoice, user=request.user)

    if result["success"]:
        invoice.status = "cancelled"
        invoice.save()
        if result.get("simulated"):
            messages.info(request, f"{invoice.invoice_number}: {result['message']}")
        else:
            messages.success(request, f"{invoice.invoice_number}: {result['message']}")
    else:
        messages.error(request, f"{invoice.invoice_number} iptal edilemedi: {result['message']}")

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
    # Yalnızca gerçekten "gönderilmiş/alınmış" (sent) durumundaki gelen faturalar
    # onaylanabilir; bir taslağı ya da zaten iptal/red edilmiş bir faturayı
    # yanlışlıkla "onaylandı" yapmanın önüne geçer.
    invoice = get_object_or_404(Invoice, id=id, user=request.user, status="sent")
    invoice.status = "approved"
    invoice.save(update_fields=["status"])
    messages.success(request, f"{invoice.invoice_number} onaylandı.")
    return _safe_redirect(request, "invoices_incoming")


@login_required
def invoice_reject(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user, status="sent")
    invoice.status = "rejected"
    invoice.save(update_fields=["status"])
    messages.warning(request, f"{invoice.invoice_number} reddedildi.")
    return _safe_redirect(request, "invoices_incoming")


@login_required
def invoice_notify_customer(request, id):
    """E-Arşiv faturasının linkini müşteriye e-posta/SMS ile gönderir (Aşama 11)."""
    invoice = get_object_or_404(Invoice, id=id, user=request.user, type="e-arsiv")
    result = notifications.notify_customer(invoice, request=request)
    if result["success"]:
        messages.success(request, result["message"])
    else:
        messages.error(request, result["message"])
    return _safe_redirect(request, "earchive_sent")


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