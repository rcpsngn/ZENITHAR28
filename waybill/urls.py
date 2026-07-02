from django.urls import path
from . import views

urlpatterns = [

    path("create/", views.irsaliye_create, name="irsaliye_create"),
    path("draft/", views.irsaliye_draft, name="irsaliye_draft"),
    path("incoming/", views.irsaliye_incoming, name="irsaliye_incoming"),
    path("sent/", views.irsaliye_sent, name="irsaliye_sent"),

]