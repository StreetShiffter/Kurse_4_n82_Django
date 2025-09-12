import secrets


from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth.views import LoginView

from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404

from django.views.generic import CreateView, UpdateView, ListView

from config.settings import EMAIL_HOST_USER
from mailservices.models import MailAttempt, Message, Sending, Client
from .forms import CustomUserCreationForm, UserProfileForm
from django.views import View
from django.urls import reverse_lazy

from .models import User


class UserRegisterView(CreateView):
    """Контроллер регистрации пользователя"""

    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

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
            recipient_list=[user.email],
        )
        # return super().form_valid(form) Важно: НЕ вызываем super().form_valid(form) - Иначе будет автологин
        messages.info(self.request, "Проверьте почту для подтверждения email.")
        return redirect(self.success_url)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)

    if user.is_active:
        # Уже активен — просто перенаправляем
        return redirect("users:login")

    # Активируем
    user.is_active = True
    user.token = None  # Обнуляем токен, что бы можно было восстановить пароль по новому токену ТРАБЛ
    user.save()

    # Можно добавить сообщение на странице логина
    messages.success(request, "Email подтверждён! Теперь можно войти.")

    return redirect("users:login")


class CustomLoginView(LoginView):
    """Контроллер входа в профиль (Использует AuthiticationCreateForm по умолчанию)"""

    template_name = "users/login.html"
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        user = form.get_user()
        if user.token:  # если токен ещё есть — обнуляем
            user.token = None
            user.save()
        return super().form_valid(form)


class UserProfileView(View):
    """Вьюшка кабинета пользователя"""

    def get(self, request):
        user = request.user
        attempts = MailAttempt.objects.filter(mailing__owner=user)

        context = {
            "user_profile": user,
            "total_attempts": attempts.count(),
            "successful_attempts": attempts.filter(status="success").count(),
            "failed_attempts": attempts.filter(status="failed").count(),
        }
        return render(request, "users/profile.html", context)


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """Вьюшка редактирования кабинета пользователя(LoginRequiredMixi защищает от неавторизованности)"""

    model = User
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user  # редактируем только текущего пользователя


##########################################################################################
# Администрирование
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Просмотр списка пользователей + статистика по сообщениям, клиентам и рассылкам"""

    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    # 🔽 Правильно: флаг должен быть атрибутом класса
    raise_exception = True

    def test_func(self):
        """Разрешаем доступ только суперпользователю - для работы UserPassedTestMixin"""
        perms_list = [
            "mailservices.can_view_all_messages",
            "mailservices.can_view_all_clients",
            "mailservices.can_view_all_sendings",
        ]
        return self.request.user.has_perms(perms_list)

    def get_queryset(self):
        """Суперпользователь видит всех, остальные — пустой queryset (доступ запрещён через test_func)"""
        return User.objects.all()  # будет вызвано только если test_func вернул True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Теперь безопасно: мы знаем, что пользователь — суперпользователь
        context["messages_list"] = Message.objects.all()
        context["sendings_list"] = Sending.objects.all()
        context["clients_list"] = Client.objects.all()
        context["title"] = "Админ-панель: Все данные"

        return context


@login_required
def toggle_user_active(request, pk):
    """Блокировка пользователя админом или модератором"""

    print("=== toggle_user_active ===")
    print("User:", request.user.username, "is_superuser:", request.user.is_superuser)
    print("Target user pk:", pk)

    if not request.user.is_superuser:
        messages.error(request, "Доступ запрещён: не суперпользователь")
        print("Доступ запрещён")
        return redirect("users:user_list")

    user = get_object_or_404(User, pk=pk)
    print("Target user:", user.username, "is_active:", user.is_active)

    # 🔒 Защита от самоблокирования
    if user.pk == request.user.pk:
        messages.error(request, "Нельзя заблокировать самого себя!")
        print("Попытка самоблокировки")
        return redirect("users:user_list")

    old_status = user.is_active
    user.is_active = not user.is_active
    user.save()
    print(f"Статус изменён: {old_status} → {user.is_active}")

    if user.is_active:
        messages.success(request, f"Пользователь {user.username} разблокирован.")
    else:
        messages.warning(request, f"Пользователь {user.username} заблокирован.")

    return redirect("users:user_list")
