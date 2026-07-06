from django.urls import path
from . import views

urlpatterns = [

    path("create/", views.waybill_create, name="waybill_create"),
    path("draft/", views.waybill_draft, name="waybill_draft"),
    path("incoming/", views.waybill_incoming, name="waybill_incoming"),
    path("sent/", views.waybill_sent, name="waybill_sent"),

]