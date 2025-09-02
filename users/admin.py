from django.contrib import admin
from django.contrib.admin.utils import help_text_for_field

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone')