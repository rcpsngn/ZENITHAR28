from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.waybill_create, name="waybill_create"),
    path("edit/<int:id>/", views.waybill_edit, name="waybill_edit"),

    path("draft/", views.waybill_draft, name="waybill_draft"),
    path("incoming/", views.waybill_incoming, name="waybill_incoming"),
    path("sent/", views.waybill_sent, name="waybill_sent"),

    path("send/<int:id>/", views.waybill_send, name="waybill_send"),
    path("cancel/<int:id>/", views.waybill_cancel, name="waybill_cancel"),
    path("delete/<int:id>/", views.waybill_delete, name="waybill_delete"),
    path("duplicate/<int:id>/", views.waybill_duplicate, name="waybill_duplicate"),
    path("approve/<int:id>/", views.waybill_approve, name="waybill_approve"),
    path("partial-accept/<int:id>/", views.waybill_partial_accept, name="waybill_partial_accept"),
    path("reject/<int:id>/", views.waybill_reject, name="waybill_reject"),

    path("toggle-read/<int:id>/", views.waybill_toggle_read, name="waybill_toggle_read"),
    path("toggle-archive/<int:id>/", views.waybill_toggle_archive, name="waybill_toggle_archive"),

    path("bulk-delete/", views.waybill_bulk_delete, name="waybill_bulk_delete"),
    path("bulk-mark-read/", views.waybill_bulk_mark_read, name="waybill_bulk_mark_read"),
    path("bulk-mark-unread/", views.waybill_bulk_mark_unread, name="waybill_bulk_mark_unread"),
]
