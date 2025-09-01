from django.contrib.auth.models import User
from django.db import models


class Client(models.Model):
    email = models.EmailField(unique=True,
                              verbose_name="Email получателя",
                              help_text="Уникальный адрес электронной почты получателя")

    full_name = models.CharField(max_length=255,
                                 verbose_name="Ф.И.О.",
                                 help_text="Полное имя получателя")

    comment = models.TextField(blank=True, null=True,
                               verbose_name="Комментарий",
                               help_text="Дополнительная информация о получателе")


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"

    def __str__(self):
        return f"{self.full_name} ({self.email})"

class Message(models.Model):
    title = models.CharField(max_length=255,
                             verbose_name="Тема письма",
                             help_text="Заголовок")

    body = models.TextField(verbose_name="Тело письма",
                            help_text="Содержание письма")


    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.title

class Sending(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_datetime = models.DateTimeField(
        verbose_name="Дата и время первой отправки"
    )
    end_datetime = models.DateTimeField(
        verbose_name="Дата и время окончания отправки"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name="Статус рассылки"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(
        Client,
        verbose_name="Получатели"
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка {self.start_datetime} — {self.status}"