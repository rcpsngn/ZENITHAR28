from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Invoice


def invoices_home(request):
    return redirect("invoices_draft")


# FATURA OLUŞTUR
@login_required
def invoices_page(request):

    if request.method == "POST":

        Invoice.objects.create(
            user=request.user,
            type=request.POST.get("type"),
            invoice_number=request.POST.get("invoice_number"),
            customer_name=request.POST.get("customer_name"),
            customer_tax_id=request.POST.get("customer_tax_id"),
            customer_address=request.POST.get("customer_address"),
            amount=request.POST.get("amount"),
            vat_rate=request.POST.get("vat_rate"),
            vat_amount=request.POST.get("vat_amount"),
            total_amount=request.POST.get("total_amount"),
            issue_date=request.POST.get("issue_date"),
            notes=request.POST.get("notes"),
            status="draft"
        )

        return redirect("invoices_draft")

    return render(request, "invoices/invoices-create.html")


# TASLAK FATURALAR
@login_required
def invoices_draft(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        status="draft"
    )

    return render(request, "invoices/invoices-draft.html", {
        "invoices": invoices
    })


# GİDEN FATURALAR
@login_required
def invoices_sent(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        status="sent"
    )

    return render(request, "invoices/invoices-sent.html", {
        "invoices": invoices
    })


# FATURA KES
@login_required
def invoice_send(request, id):

    invoice = get_object_or_404(
        Invoice,
        id=id,
        user=request.user
    )

    invoice.status = "sent"
    invoice.save()

    return redirect("invoices_sent")


# FATURA SİL
@login_required
def invoice_delete(request, id):

    invoice = get_object_or_404(
        Invoice,
        id=id,
        user=request.user
    )

    invoice.delete()

    return redirect("invoices_draft")


# GELEN E-FATURA
@login_required
def invoices_incoming(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-fatura"
    )

    return render(request, "invoices/invoices-incoming.html", {
        "invoices": invoices
    })


# GELEN E-ARŞİV FATURALAR
@login_required
def earchive_incoming(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-arsiv",
        status="incoming"
    )

    return render(request, "invoices/invoices-earchive-incoming.html", {
        "invoices": invoices
    })


# GİDEN E-ARŞİV FATURALAR
@login_required
def earchive_sent(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-arsiv",
        status="sent"
    )

    return render(request, "invoices/invoices-earchive-sent.html", {
        "invoices": invoices
    })