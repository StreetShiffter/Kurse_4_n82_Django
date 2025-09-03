# mailservices/urls.py
from django.urls import path
from . import views
from .apps import MailservicesConfig

app_name = MailservicesConfig.name  # → 'mailservices'

urlpatterns = [
    path("", views.home_view, name="home"),
    path("clients/create/", views.ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>", views.ClientDetailView.as_view(), name="client_detail"),
    path("clients/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client_edit"),
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("messages/", views.MessageListView.as_view(), name="message_list"),
    path("mailings/", views.SendingListView.as_view(), name="mailing_list"),
    # ... другие закомментированные пути
]

# urlpatterns = [
#     path("", views.home_view, name="home"),
#     # Recipient URLs
#     path("recipients/", views.RecipientListView.as_view(), name="recipient_list"),
#     # path("recipients/create/", views.RecipientCreateView.as_view(), name="recipient_create"),
#     # path("recipients/<int:pk>/edit/", views.RecipientUpdateView.as_view(), name="recipient_update"),
#     # path("recipients/<int:pk>/delete/", views.RecipientDeleteView.as_view(), name="recipient_delete"),
#     # Message URLs
#     path("messages/", views.MessageListView.as_view(), name="message_list"),
#     # path("messages/create/", views.MessageCreateView.as_view(), name="message_create"),
#     # path("messages/<int:pk>/edit/", views.MessageUpdateView.as_view(), name="message_update"),
#     # path("messages/<int:pk>/delete/", views.MessageDeleteView.as_view(), name="message_delete"),
#     # Mailing URLs
#     path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
#     # path("mailings/create/", views.MailingCreateView.as_view(), name="mailing_create"),
#     # path("mailings/<int:pk>/edit/", views.MailingUpdateView.as_view(), name="mailing_update"),
#     # path("mailings/<int:pk>/delete/", views.MailingDeleteView.as_view(), name="mailing_delete"),
# ]
