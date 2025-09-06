from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone

from mailservices.models import Client, Message, Sending
from mailservices.utils import CENSORED_WORDS


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email',
                  'full_name',
                  'comment',
                  ]

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Почта пользователя'})

        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Полное имя пользователя, например Иванов Иван Иванович'})

        self.fields['comment'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Комментарий по пользователю'})

    def clean_email(self):
        """Валидатор корректного email"""
        email = self.cleaned_data['email']

        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError('Введите корректный email-адрес.')
        return email

    def clean_full_name(self):
        """Валидатор корректного  full_name """
        full_name = self.cleaned_data.get('full_name')

        if full_name:
            # Убираем пробелы по краям
            full_name_stripped = full_name.strip()

            if not full_name_stripped.replace(' ', '').isalpha():
                raise ValidationError('Имя должно состоять только из букв и пробелов.')

            if not full_name_stripped:
                raise ValidationError('Имя не может быть пустым или состоять только из пробелов.')
        else:
            raise ValidationError('Имя обязательно для заполнения.')

        return full_name

    def clean_comment(self):
        """Валидатор корректности описания"""
        comment = self.cleaned_data.get('comment', '')
        if not comment.strip():
            return comment

        lower_comment = comment.lower()
        for word in CENSORED_WORDS:
            if word in lower_comment:
                raise ValidationError(f'Использовано запрещённое слово: "{word}"')
        return comment


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title',
                  'body',
                  ]

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Тема письма'})

        self.fields['body'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Тело письма'})

    def clean_title(self):
        """Валидатор корректности названия письма"""
        title = self.cleaned_data.get('title', '')
        if not title.strip():
            return title

        lower_title = title.lower()
        for word in CENSORED_WORDS:
            if word in lower_title:
                raise ValidationError(f'Использовано запрещённое слово: "{word}"')
        return title

    def clean_body(self):
        """Валидатор корректности наполнения письма"""
        body = self.cleaned_data.get('body', '')
        if not body.strip():
            return body

        lower_body = body.lower()
        for word in CENSORED_WORDS:
            if word in lower_body:
                raise ValidationError(f'Использовано запрещённое слово: "{word}"')
        return body

class SendingForm(forms.ModelForm):
    class Meta:
        model = Sending
        fields = ['start_datetime',
                  'end_datetime',
                  'message',
                  'recipients'
                  ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),}

    def __init__(self, *args, **kwargs):
        super(SendingForm, self).__init__(*args, **kwargs)
        self.fields['start_datetime'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Начало рассылки'})

        self.fields['end_datetime'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Конец рассылки'})

        self.fields['message'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Сообщение для рассылки'})

        self.fields['recipients'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Получатели рассылки (для добавления нескольких удерживайте CTRL)'})

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_datetime")
        end = cleaned_data.get("end_datetime")

        if start and not timezone.is_aware(start):
            # Приводим к timezone-aware (UTC)
            cleaned_data["start_datetime"] = timezone.make_aware(start, timezone.get_current_timezone())

        if end and not timezone.is_aware(end):
            cleaned_data["end_datetime"] = timezone.make_aware(end, timezone.get_current_timezone())

        return cleaned_data


