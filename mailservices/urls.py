# mailservices/urls.py
from django.urls import path
from . import views
from .apps import MailservicesConfig

app_name = MailservicesConfig.name  # → 'mailservices'

urlpatterns = [
    path("", views.home_view, name="home"),
    path("recipients/", views.ClientListView.as_view(), name="recipient_list"),
    path("messages/", views.MessageListView.as_view(), name="message_list"),
    path("mailings/", views.SendingListView.as_view(), name="mailing_list"),
    # ... другие закомментированные пути
]