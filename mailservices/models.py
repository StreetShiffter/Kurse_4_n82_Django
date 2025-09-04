# from django.contrib.auth.models import User

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Client(models.Model):
    '''Получатель рассылки'''
    email = models.EmailField(unique=True,
                              verbose_name="Email получателя",
                              help_text="Уникальный адрес электронной почты получателя")

    full_name = models.CharField(max_length=255,
                                 verbose_name="Ф.И.О.",
                                 help_text="Полное имя получателя")

    comment = models.TextField(blank=True, null=True,
                               verbose_name="Комментарий",
                               help_text="Дополнительная информация о получателе")

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              verbose_name="Владелец")


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"

    def __str__(self):
        return f"{self.full_name} ({self.email})"

class Message(models.Model):
    '''Сообщение для рассылки'''
    title = models.CharField(max_length=255,
                             verbose_name="Тема письма",
                             help_text="Заголовок")

    body = models.TextField(verbose_name="Тело письма",
                            help_text="Содержание письма")

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              verbose_name="Владелец")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.title

class Sending(models.Model):
    '''Отправка рассылки'''
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
        verbose_name="Получатели рассылки (для добавления нескольких удерживайте CTRL)"
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              verbose_name="Владелец")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def clean(self):
        super().clean()

        if self.start_datetime and self.end_datetime:
            if self.start_datetime >= self.end_datetime:
                raise ValidationError({
                    'end_datetime': 'Дата окончания должна быть позже даты начала.'
                })

            if self.start_datetime < timezone.now():
                raise ValidationError({
                    'start_datetime': 'Дата начала не может быть в прошлом.'
                })

            if (self.end_datetime - self.start_datetime).days > 365:
                raise ValidationError({
                    'end_datetime': 'Рассылка не может длиться больше года.'
                })

    def __str__(self):
        return f"Рассылка {self.start_datetime} — {self.status}"



class MailAttempt(models.Model):
    '''Статистика попытки рассылки'''
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    attempt_datetime = models.DateTimeField(
        auto_now_add=True,  # Автоматически устанавливается при создании
        verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name="Статус попытки"
    )
    server_response = models.TextField(
        blank=True, null=True,
        verbose_name="Ответ почтового сервера",
        help_text="Ответ от SMTP-сервера при отправке"
    )
    mailing = models.ForeignKey(
        Sending,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Рассылка"
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ['-attempt_datetime']  # Сортировка по убыванию даты

    def __str__(self):
        return f"Попытка: {self.mailing} — {self.get_status_display()} ({self.attempt_datetime})"