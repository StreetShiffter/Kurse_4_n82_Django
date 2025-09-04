# mailservices/urls.py
from django.urls import path
from . import views
from .apps import MailservicesConfig

app_name = MailservicesConfig.name  # → 'mailservices'

urlpatterns = [
    path("", views.home_view, name="home"),
    path("clients/create/", views.ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("clients/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client_edit"),
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/<int:pk>/delete/", views.ClientDeleteView.as_view(), name="client_delete"),
    ######################
    path("messages/create/", views.MessageCreateView.as_view(), name="message_create"),
    path("messages/", views.MessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/edit/", views.MessageUpdateView.as_view(), name="message_edit"),
    path("messages/<int:pk>/delete/", views.MessageDeleteView.as_view(), name="message_delete"),
    path("messages/<int:pk>/", views.MessageDetailView.as_view(), name="message_detail"),
    path("sending/", views.SendingListView.as_view(), name="sending_list")
]
