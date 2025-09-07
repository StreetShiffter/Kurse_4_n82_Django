# mailservices/admin.py
from django.contrib import admin
from .models import Client, Message, Sending, MailAttempt


class OwnerFilteredAdmin(admin.ModelAdmin):
    """
    Админка, которая показывает все объекты суперпользователю,
    и только объекты, принадлежащие пользователю, — обычным пользователям.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)


@admin.register(Client)
class ClientAdmin(OwnerFilteredAdmin):
    list_display = ('id', 'email', 'full_name', 'owner')
    search_fields = ('email', 'full_name')

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ('owner',)  # Можно фильтровать, но по умолчанию — всё
        return ()  # Обычный пользователь не видит фильтр

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        print("🔸 Пользователь:", request.user.email)
        print("🔸 Is superuser:", request.user.is_superuser)
        print("🔸 URL параметры:", dict(request.GET))
        print("🔸 Всего в БД:", qs.count())
        if request.user.is_superuser:
            print("✅ Возвращаем ВСЁ")
            return qs
        print("👤 Фильтруем по owner")
        return qs.filter(owner=request.user)


@admin.register(Message)
class MessageAdmin(OwnerFilteredAdmin):
    list_display = ('id', 'title', 'owner')
    list_filter = ('owner',)
    search_fields = ('title',)


@admin.register(Sending)
class SendingAdmin(OwnerFilteredAdmin):
    list_display = ('id', 'start_datetime', 'end_datetime', 'status', 'owner')
    list_filter = ('status', 'owner', 'start_datetime', 'end_datetime')
    search_fields = ('status', 'start_datetime', 'end_datetime')


@admin.register(MailAttempt)
class MailAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt_datetime', 'status', 'mailing', 'owner')
    list_filter = ('status',)
    search_fields = ('status', 'attempt_datetime')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(mailing__owner=request.user)

    @admin.display(description='Владелец')
    def owner(self, obj):
        return obj.mailing.owner
    owner.admin_order_field = 'mailing__owner'