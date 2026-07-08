from django.urls import path
from . import views

urlpatterns = [
    path("", views.invoices_home, name="invoices"),
    path("create/", views.invoices_page, name="invoices_create"),
    path("edit/<int:id>/", views.invoice_edit, name="invoice_edit"),
    path("draft/", views.invoices_draft, name="invoices_draft"),
    path("sent/", views.invoices_sent, name="invoices_sent"),
    path("incoming/", views.invoices_incoming, name="invoices_incoming"),
    path("earchive/incoming/", views.earchive_incoming, name="earchive_incoming"),
    path("earchive/sent/", views.earchive_sent, name="earchive_sent"),
    path("send/<int:id>/", views.invoice_send, name="invoice_send"),
    path("cancel/<int:id>/", views.invoice_cancel, name="invoice_cancel"),
    path("delete/<int:id>/", views.invoice_delete, name="invoice_delete"),
    path("duplicate/<int:id>/", views.invoice_duplicate, name="invoice_duplicate"),
    path("bulk-delete/", views.invoices_bulk_delete, name="invoices_bulk_delete"),
    path("toggle-read/<int:id>/", views.invoice_toggle_read, name="invoice_toggle_read"),
    path("toggle-archive/<int:id>/", views.invoice_toggle_archive, name="invoice_toggle_archive"),
    path("approve/<int:id>/", views.invoice_approve, name="invoice_approve"),
    path("reject/<int:id>/", views.invoice_reject, name="invoice_reject"),
    path("bulk-mark-read/", views.invoices_bulk_mark_read, name="invoices_bulk_mark_read"),
    path("bulk-mark-unread/", views.invoices_bulk_mark_unread, name="invoices_bulk_mark_unread"),

    # Yeni Eklenen API ve Detay Görüntüleme Rotaları
    path("view/<int:id>/", views.invoice_view, name="invoice_view"),
    path("api/get-tcmb-rate/", views.get_tcmb_rate, name="get_tcmb_rate"),
    path("api/vkn-sorgula/", views.vkn_sorgula, name="vkn_sorgula"),
]