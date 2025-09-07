import secrets

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, UpdateView

from config.settings import EMAIL_HOST_USER
from .forms import CustomUserCreationForm, UserProfileForm
from django.views import View
from django.urls import reverse_lazy, reverse

from .models import User


class UserRegisterView(CreateView):
    '''Контроллер регистрации пользователя'''
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)  # Сохраняем пользователя без логирования
        user.is_active = False  # Деактивируем
        token = secrets.token_hex(16)  # Генерация токена
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        # return super().form_valid(form) Важно: НЕ вызываем super().form_valid(form) - Иначе будет автологин
        messages.info(self.request, 'Проверьте почту для подтверждения email.')
        return redirect(self.success_url)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)

    if user.is_active:
        # Уже активен — просто перенаправляем
        return redirect('users:login')

    # Активируем
    user.is_active = True
    user.token = None  # Обнуляем токен, что бы можно было восстановить пароль по новому токену ТРАБЛ
    user.save()

    # Можно добавить сообщение на странице логина
    messages.success(request, 'Email подтверждён! Теперь можно войти.')

    return redirect('users:login')


class CustomLoginView(LoginView):
    '''Контроллер входа в профиль (Использует AuthiticationCreateForm по умолчанию)'''
    template_name = 'users/login.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        user = form.get_user()
        if user.token:  # если токен ещё есть — обнуляем
            user.token = None
            user.save()
        return super().form_valid(form)


class UserProfileView(View):
    '''Вьюшка кабинета пользователя'''

    def get(self, request):
        return render(request, 'users/profile.html')


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    '''Вьюшка редактирования кабинета пользователя(LoginRequiredMixi защищает от неавторизованности)'''
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user  # редактируем только текущего пользователя