from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailservices.models import Sending, Message, Client


class Command(BaseCommand):
    help = 'Создает группу "Менеджеры" с необходимыми правами'

    def handle(self, *args, **kwargs):
        # Создание группы
        group, created = Group.objects.get_or_create(name="Менеджеры")

        # Назначение прав для модели Sending
        mailing_content_type = ContentType.objects.get_for_model(Sending)
        mailing_permissions = Permission.objects.filter(
            content_type=mailing_content_type, codename__in=["can_view_all_sendings"]
        )
        group.permissions.add(*mailing_permissions)

        # Назначение прав для модели Message
        message_content_type = ContentType.objects.get_for_model(Message)
        message_permissions = Permission.objects.filter(
            content_type=message_content_type, codename__in=["can_view_all_messages"]
        )
        group.permissions.add(*message_permissions)

        # Назначение прав для модели Client
        recipient_content_type = ContentType.objects.get_for_model(Client)
        recipient_permissions = Permission.objects.filter(
            content_type=recipient_content_type,
            codename__in=["can_view_all_clients"],
        )
        group.permissions.add(*recipient_permissions)

        self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" успешно создана!'))
