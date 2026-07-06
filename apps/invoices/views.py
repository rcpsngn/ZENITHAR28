from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Invoice, InvoiceItem
import uuid
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal


def invoices_home(request):
    return redirect("invoices_draft")


# API: TCMB CANLI DÖVİZ KURU ÇEKİCİ
def get_tcmb_rate(request):
    currency_code = request.GET.get("code", "TL").upper()
    if currency_code in ["TL", "TRY"]:
        return JsonResponse({"rate": "1.0000"})
    try:
        req = urllib.request.Request(
            "https://www.tcmb.gov.tr/kurlar/today.xml",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        for currency in root.findall('Currency'):
            if currency.get('CurrencyCode') == currency_code:
                rate_str = currency.find('ForexBuying').text
                return JsonResponse({"rate": str(round(float(rate_str), 4))})
    except Exception:
        fallbacks = {"USD": "34.2500", "EUR": "37.1200", "GBP": "44.5000"}
        return JsonResponse({"rate": fallbacks.get(currency_code, "1.0000")})
    return JsonResponse({"rate": "1.0000"})


# API: GİB VERGİ DAİRESİ OTOMATİK SORGULAMA SİMÜLASYONU
def vkn_sorgula(request):
    vkn = request.GET.get("vkn", "")
    if vkn == "1234567890":
        return JsonResponse({
            "success": True,
            "title": "ZENITHAR YAZILIM VE TEKNOLOJİ ANONİM ŞİRKETİ",
            "office": "BEYOĞLU VERGİ DAİRESİ",
            "city": "İSTANBUL", "district": "BEYOĞLU",
            "street": "İSTİKLAL CADDESİ NO:100 KAT:3", "zip": "34430"
        })
    return JsonResponse({"success": False, "message": "Mükellef bulunamadı. Lütfen bilgileri elle doldurunuz."})


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
            exchange_rate=Decimal(request.POST.get("exchange_rate", "1.0000") or "1.0000"),
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
                    quantity=Decimal(str(item.get("qty"))),
                    unit=item.get("unit"),
                    unit_price=Decimal(str(item.get("price"))),
                    vat_rate=Decimal(str(item.get("vat")))
                )
        except Exception:
            pass

        return redirect("invoices_draft")

    return render(request, "invoices/invoices-create.html")


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
    invoice.status = "sent"
    invoice.save()
    return redirect("invoices_sent")


@login_required
def invoice_delete(request, id):
    invoice = get_object_or_404(Invoice, id=id, user=request.user)
    invoice.delete()
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