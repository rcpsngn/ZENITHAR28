from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from invoices.models import Invoice


@login_required
def irsaliye_create(request):
    return render(request,"eirsaliye/irsaliye-create.html")


@login_required
def irsaliye_draft(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-irsaliye",
        status="draft"
    )

    return render(request,"eirsaliye/irsaliye-draft.html",{
        "invoices": invoices
    })


@login_required
def irsaliye_incoming(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-irsaliye",
        status="incoming"
    )

    return render(request,"eirsaliye/irsaliye-incoming.html",{
        "invoices": invoices
    })


@login_required
def irsaliye_sent(request):

    invoices = Invoice.objects.filter(
        user=request.user,
        type="e-irsaliye",
        status="sent"
    )

    return render(request,"eirsaliye/irsaliye-sent.html",{
        "invoices": invoices
    })