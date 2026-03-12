from django.urls import path
from . import views

urlpatterns = [

    path("", views.invoices_home, name="invoices"),

    path("create/", views.invoices_page, name="invoices_create"),
    path("draft/", views.invoices_draft, name="invoices_draft"),
    path("sent/", views.invoices_sent, name="invoices_sent"),

    path("incoming/", views.invoices_incoming, name="invoices_incoming"),

    path("earchive/incoming/", views.earchive_incoming, name="earchive_incoming"),
    path("earchive/sent/", views.earchive_sent, name="earchive_sent"),

    path("send/<int:id>/", views.invoice_send, name="invoice_send"),
    path("delete/<int:id>/", views.invoice_delete, name="invoice_delete"),
]
