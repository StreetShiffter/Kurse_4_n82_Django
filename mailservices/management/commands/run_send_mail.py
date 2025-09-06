from django.core.management.base import BaseCommand
from django.utils import timezone
from mailservices.models import Sending
from mailservices.services import send_mailing  # ← ваша функция


class Command(BaseCommand):
    help = 'Автоматическая обработка всех активных рассылок: запуск и завершение'

    def handle(self, *args, **options):
        now = timezone.now()

        # 1. Завершаем рассылки, у которых время истекло
        completed_count = Sending.objects.filter(
            status='started',
            end_datetime__lt=now
        ).update(status='completed')

        if completed_count:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Завершено {completed_count} рассылок по времени')
            )

        # 2. Находим рассылки, которые нужно запустить:
        #    - статус 'created'
        #    - время начала <= текущего
        #    - время окончания ещё не прошло
        mailings_to_start = Sending.objects.filter(
            status='created',
            start_datetime__lte=now,
            end_datetime__gt=now
        )

        for mailing in mailings_to_start:
            self.stdout.write(f'🚀 Запускаем рассылку ID={mailing.pk} — {mailing}')
            send_mailing(mailing)  # ← используем вашу функцию

        # 3. Также можно обработать "зависшие" рассылки, которые уже должны быть завершены
        #    (на случай, если не сработало update выше)
        for mailing in Sending.objects.filter(status='started', end_datetime__lt=now):
            self.stdout.write(f'🔚 Принудительно завершаем рассылку ID={mailing.pk}')
            send_mailing(mailing)  # внутри проверит время и завершит

        self.stdout.write(self.style.SUCCESS('✅ Автоматическая обработка рассылок завершена'))