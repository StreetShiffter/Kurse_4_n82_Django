from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from mailservices.models import Client
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




