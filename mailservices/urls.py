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
    path("sending/", views.SendingListView.as_view(), name="sending_list"),
    path("sending/<int:pk>/delete/", views.SendingDeleteView.as_view(), name="sending_delete"),
    path("sending/create/", views.SendingCreateView.as_view(), name="sending_create"),
    path("sending/<int:pk>/", views.SendingDetailView.as_view(), name="sending_detail"),
    path("sending/<int:pk>/edit/", views.SendingUpdateView.as_view(), name="sending_edit"),
    path('attempts/', views.AttemptListView.as_view(), name='attempt_list'),
    path('<int:pk>/send/', views.SendingNowView.as_view(), name='send_mailing_now'),
    #####################################################################################
    #Администрирование
    path('users/<int:user_id>/clients/', views.UserClientListView.as_view(), name='user_client_list'),
    path('users/<int:user_id>/messages/', views.UserMessageListView.as_view(), name='user_message_list'),
    path('users/<int:user_id>/sendings/', views.UserSendingListView.as_view(), name='user_sending_list'),
    path('users/toggle-sending/<int:pk>/', views.toggle_user_block_sending, name='toggle_user_block_sending'),
]
