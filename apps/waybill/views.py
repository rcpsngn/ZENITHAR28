from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
import uuid
from datetime import datetime, timedelta

from apps.invoices.models import Invoice, InvoiceItem
from apps.invoices.views import to_decimal, generate_invoice_number, _safe_redirect

# Aşama 14 notu: "Fiili sevk tarihi ve saati doğrulama kontrolleri (Geçmişe
# dönük irsaliye kısıtı) backend'e eklenmeli." Bir irsaliye ne gelecekte bir
# tarihte düzenlenebilir (henüz sevk edilmemiş bir malın irsaliyesi olmaz) ne
# de makul bir süreden daha eskiye tarihlenebilir (usulsüz geçmişe dönük
# belge düzenlemeyi/kayıt dışını önlemek için).
MAX_BACKDATE_DAYS = 7


def _validate_waybill_date(issue_date):
    """
    issue_date: str ("YYYY-MM-DD") ya da date nesnesi olabilir.
    Geçerliyse None, geçersizse kullanıcıya gösterilecek hata mesajını döner.
    """
    if not issue_date:
        return None
    if isinstance(issue_date, str):
        try:
            issue_date = datetime.strptime(issue_date, "%Y-%m-%d").date()
        except ValueError:
            return "Sevk tarihi formatı geçersiz."

    today = datetime.now().date()
    if issue_date > today:
        return "Sevk tarihi gelecekte bir tarih olamaz."
    if issue_date < today - timedelta(days=MAX_BACKDATE_DAYS):
        return f"Sevk tarihi bugünden en fazla {MAX_BACKDATE_DAYS} gün geriye tarihlenebilir."
    return None


# ---- OLUŞTUR / DÜZENLE ----

@login_required
def waybill_create(request):
    if request.method == "POST":
        issue_date = request.POST.get("date") or datetime.now().date()
        date_error = _validate_waybill_date(issue_date)
        if date_error:
            messages.error(request, date_error)
            return render(request, "waybill/waybill-create.html", {"active_tab": "create"})

        waybill = Invoice.objects.create(
            user=request.user,
            ettn=str(uuid.uuid4()),
            custom_no="TR1.2",
            invoice_number=generate_invoice_number("IRS"),
            type="e-irsaliye",
            invoice_type=request.POST.get("invoice_type", "satis"),
            issue_date=issue_date,
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
            notes=request.POST.get("notes", ""),
            status="draft",
        )

        items_json = request.POST.get("items_json_data", "[]")
        try:
            for item in json.loads(items_json):
                InvoiceItem.objects.create(
                    invoice=waybill,
                    description=item.get("desc"),
                    quantity=to_decimal(item.get("qty"), "1"),
                    unit=item.get("unit"),
                    unit_price=to_decimal(item.get("price"), "0"),
                    vat_rate=to_decimal(item.get("vat"), "0"),
                )
        except Exception:
            pass

        return redirect("waybill_draft")

    return render(request, "waybill/waybill-create.html", {"active_tab": "create"})


@login_required
def waybill_edit(request, id):
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye", status="draft")

    if request.method == "POST":
        issue_date = request.POST.get("date") or waybill.issue_date
        date_error = _validate_waybill_date(issue_date)
        if date_error:
            messages.error(request, date_error)
            items_json = json.dumps([
                {
                    "desc": item.description, "qty": float(item.quantity), "unit": item.unit,
                    "price": float(item.unit_price), "vat": float(item.vat_rate),
                }
                for item in waybill.items.all()
            ])
            return render(request, "waybill/waybill-create.html", {
                "invoice": waybill, "items_json": items_json, "active_tab": "draft",
            })

        waybill.invoice_type = request.POST.get("invoice_type", waybill.invoice_type)
        waybill.issue_date = issue_date
        waybill.currency = request.POST.get("currency", waybill.currency)
        waybill.exchange_rate = to_decimal(request.POST.get("exchange_rate"), "1.0000")
        waybill.customer_name = request.POST.get("customer_name")
        waybill.customer_tax_id = request.POST.get("customer_tax_id", "")
        waybill.customer_tax_office = request.POST.get("customer_tax_office", "")
        waybill.customer_first_name = request.POST.get("customer_first_name", "")
        waybill.customer_last_name = request.POST.get("customer_last_name", "")
        waybill.customer_country = request.POST.get("customer_country", "Türkiye")
        waybill.customer_city = request.POST.get("customer_city", "")
        waybill.customer_district = request.POST.get("customer_district", "")
        waybill.customer_street = request.POST.get("customer_street", "")
        waybill.customer_postal_code = request.POST.get("customer_postal_code", "")
        waybill.notes = request.POST.get("notes", "")
        waybill.save()

        waybill.items.all().delete()
        items_json = request.POST.get("items_json_data", "[]")
        try:
            for item in json.loads(items_json):
                InvoiceItem.objects.create(
                    invoice=waybill,
                    description=item.get("desc"),
                    quantity=to_decimal(item.get("qty"), "1"),
                    unit=item.get("unit"),
                    unit_price=to_decimal(item.get("price"), "0"),
                    vat_rate=to_decimal(item.get("vat"), "0"),
                )
        except Exception:
            pass

        return redirect("waybill_draft")

    items_json = json.dumps([
        {
            "desc": item.description,
            "qty": float(item.quantity),
            "unit": item.unit,
            "price": float(item.unit_price),
            "vat": float(item.vat_rate),
        }
        for item in waybill.items.all()
    ])

    return render(request, "waybill/waybill-create.html", {"invoice": waybill, "items_json": items_json, "active_tab": "draft"})


# ---- LİSTELER ----

@login_required
def waybill_draft(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-irsaliye", status="draft", is_archived=False)
    return render(request, "waybill/waybill-draft.html", {"invoices": invoices, "active_tab": "draft"})


@login_required
def waybill_incoming(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-irsaliye", is_archived=False).exclude(status="draft")
    unread_count = invoices.filter(is_read=False).count()
    return render(request, "waybill/waybill-incoming.html", {
        "invoices": invoices, "active_tab": "incoming", "unread_count": unread_count,
    })


@login_required
def waybill_sent(request):
    invoices = Invoice.objects.filter(user=request.user, type="e-irsaliye", status="sent", is_archived=False)
    return render(request, "waybill/waybill-sent.html", {"invoices": invoices, "active_tab": "sent"})


# ---- İŞLEMLER (fatura modülüyle aynı mantık) ----

@login_required
def waybill_send(request, id):
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye")
    waybill.status = "sent"
    waybill.save(update_fields=["status"])
    return redirect("waybill_sent")


@login_required
def waybill_cancel(request, id):
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye", status="sent")
    waybill.status = "cancelled"
    waybill.save(update_fields=["status"])
    return redirect("waybill_sent")


@login_required
def waybill_delete(request, id):
    """Sadece TASLAK irsaliyeler silinebilir. Gönderilmiş irsaliye asla silinmez, sadece iptal edilir."""
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye", status="draft")
    waybill.delete()
    return redirect("waybill_draft")


@login_required
def waybill_duplicate(request, id):
    original = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye")

    new_waybill = Invoice.objects.create(
        user=request.user,
        ettn=str(uuid.uuid4()),
        custom_no=original.custom_no,
        type="e-irsaliye",
        invoice_type=original.invoice_type,
        invoice_number=generate_invoice_number("IRS"),
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
            invoice=new_waybill,
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            vat_rate=item.vat_rate,
        )

    new_waybill.update_totals()
    return redirect("waybill_draft")


@login_required
def waybill_approve(request, id):
    """Tam kabul: yalnızca 'sent' durumundaki (henüz karar verilmemiş) irsaliyeler kabul edilebilir."""
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye", status="sent")
    waybill.status = "approved"
    waybill.save(update_fields=["status"])
    messages.success(request, f"{waybill.invoice_number} kabul edildi.")
    return _safe_redirect(request, "waybill_incoming")


@login_required
def waybill_partial_accept(request, id):
    """
    Kısmi kabul: sevk edilen malın bir kısmı kabul edilmemiş demektir (ör. eksik/hasarlı ürün).
    Muhasebe tarafında normal 'approved' irsaliyeden ayrı işlenmesi gerektiği için
    ayrı bir durum (partially_accepted) kullanılıyor.
    """
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye", status="sent")
    note = request.POST.get("partial_note", "").strip()
    waybill.status = "partially_accepted"
    if note:
        waybill.notes = (waybill.notes + "\n" if waybill.notes else "") + f"[Kısmi Kabul Notu] {note}"
        waybill.save(update_fields=["status", "notes"])
    else:
        waybill.save(update_fields=["status"])
    messages.warning(request, f"{waybill.invoice_number} kısmi kabul olarak işaretlendi.")
    return _safe_redirect(request, "waybill_incoming")


@login_required
def waybill_reject(request, id):
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye", status="sent")
    waybill.status = "rejected"
    waybill.save(update_fields=["status"])
    messages.error(request, f"{waybill.invoice_number} reddedildi.")
    return _safe_redirect(request, "waybill_incoming")


@login_required
def waybill_toggle_read(request, id):
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye")
    waybill.is_read = not waybill.is_read
    waybill.save(update_fields=["is_read"])
    return _safe_redirect(request, "waybill_incoming")


@login_required
def waybill_toggle_archive(request, id):
    waybill = get_object_or_404(Invoice, id=id, user=request.user, type="e-irsaliye")
    waybill.is_archived = not waybill.is_archived
    waybill.save(update_fields=["is_archived"])
    return _safe_redirect(request, "waybill_incoming")


@login_required
def waybill_bulk_delete(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        Invoice.objects.filter(id__in=ids, user=request.user, type="e-irsaliye", status="draft").delete()
    return redirect("waybill_draft")


@login_required
def waybill_bulk_mark_read(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        Invoice.objects.filter(id__in=ids, user=request.user, type="e-irsaliye").update(is_read=True)
    return _safe_redirect(request, "waybill_incoming")


@login_required
def waybill_bulk_mark_unread(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        Invoice.objects.filter(id__in=ids, user=request.user, type="e-irsaliye").update(is_read=False)
    return _safe_redirect(request, "waybill_incoming")
