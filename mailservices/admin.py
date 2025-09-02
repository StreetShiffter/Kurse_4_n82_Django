from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.admin.utils import help_text_for_field

from mailservices.models import Client, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'owner')



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner',)
    list_filter = ('owner',)
    search_fields = ('title',)

