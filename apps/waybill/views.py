from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.invoices.models import Invoice


@login_required
def waybill_create(request):
    return render(request,"waybill/waybill-create.html")


@login_required
def waybill_draft(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-irsaliye",
        status="draft"
    )

    return render(request,"waybill/waybill-draft.html",{
        "invoices": invoices
    })


@login_required
def waybill_incoming(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-irsaliye",
        status="incoming"
    )

    return render(request,"waybill/waybill-incoming.html",{
        "invoices": invoices
    })


@login_required
def waybill_sent(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-irsaliye",
        status="sent"
    )

    return render(request,"waybill/waybill-sent.html",{
        "invoices": invoices
    })