from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.admin.utils import help_text_for_field

from mailservices.models import Client, Message, Sending, MailAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    '''Получатели рассылки'''
    list_display = ('id', 'email', 'full_name', 'owner')



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    '''Сообщения'''
    list_display = ('id', 'title', 'owner',)
    list_filter = ('owner',)
    search_fields = ('title',)


@admin.register(Sending)
class SendingAdmin(admin.ModelAdmin):
    '''Рассылки'''
    list_display = ('id', 'start_datetime', 'end_datetime',)
    list_filter = ('owner', 'status', 'start_datetime', 'end_datetime',)
    search_fields = ('status', 'start_datetime', 'end_datetime',)


@admin.register(MailAttempt)
class MailAttemptAdmin(admin.ModelAdmin):
    '''Попытки рассылки'''
    list_display = ('id', 'attempt_datetime', 'status', 'server_response', 'mailing')
    list_filter = ('status',)
    search_fields = ('status', 'attempt_datetime',)


