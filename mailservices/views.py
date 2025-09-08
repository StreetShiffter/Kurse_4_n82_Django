from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy

from users.models import User
from .forms import ClientForm, MessageForm, SendingForm
from .models import Sending, Message, Client, MailAttempt
from .services import send_mailing


def home_view(request):
    # Общая статистика (видна всем)
    total_sendings = Sending.objects.count()
    unique_clients = Client.objects.count()

    # Активные рассылки: started или created (тоже общая или по владельцу)
    active_sendings = Sending.objects.filter(
        status__in=['created', 'started']
    ).count()

    # Если пользователь авторизован — показываем его статистику
    if request.user.is_authenticated:
        my_total = Sending.objects.filter(owner=request.user).count()
        my_active = Sending.objects.filter(
            owner=request.user,
            status__in=['created', 'started']
        ).count()
    else:
        my_total = 0
        my_active = 0

    context = {
        'total_sendings': total_sendings,
        'active_sendings': active_sendings,
        'unique_clients': unique_clients,
        # Опционально: свои показатели
        'my_total': my_total,
        'my_active': my_active,
    }
    return render(request, 'mailservices/home.html', context)

##########################################################################################

# Client CRUD
class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создание записи о клиенте"""
    model = Client
    form_class = ClientForm
    template_name = "mailservices/client_form.html"
    success_url = reverse_lazy("mailservices:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientDetailView(LoginRequiredMixin, DetailView):
    """Просмотр записи о клиенте"""
    model = Client
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование записи клиента"""
    model = Client
    form_class = ClientForm
    template_name = "mailservices/client_form.html"
    success_url = reverse_lazy("mailservices:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientListView(LoginRequiredMixin, ListView):
    """Просмотр всех записей клиентов"""
    model = Client
    template_name = "mailservices/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.has_perm('mailservices.can_view_all_clients'):
            return Client.objects.all()  # Админ видит всех
        return Client.objects.filter(owner=user)  # Обычный пользователь — только свои

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление записи клиента"""
    model = Client
    template_name = "mailservices/client_confirm_delete.html"
    success_url = reverse_lazy('mailservices:client_list')

#################################################################################

# Message CRUD
class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание сообщения"""
    model = Message
    form_class = MessageForm
    template_name = "mailservices/message_form.html"
    success_url = reverse_lazy("mailservices:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MessageListView(LoginRequiredMixin, ListView):
    """Просмотр всех сообщений"""
    model = Message
    template_name = "mailservices/message_list.html"
    context_object_name = "messages"


    def get_queryset(self):
        if self.request.user.is_superuser:
            return Message.objects.all()  # Админ видит всех
        return Message.objects.filter(owner=self.request.user)  # Обычный пользователь — только свои

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование сообщения для рассылки"""
    model = Message
    form_class = MessageForm
    template_name = "mailservices/message_form.html"
    success_url = reverse_lazy("mailservices:message_list")

class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения для рассылки"""
    model = Message
    template_name = "mailservices/message_confirm_delete.html"
    success_url = reverse_lazy("mailservices:message_list")

class MessageDetailView(LoginRequiredMixin, DetailView):
    """Просмотр сообщения для рассылки"""
    model = Message
    context_object_name = "message"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
################################################################################################

# Sending CRUD

class SendingListView(LoginRequiredMixin, ListView):
    """Просмотр списка рассылок"""
    model = Sending
    template_name = "mailservices/sending_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        # находим запись и если она есть  по времени завершения — автоматически завершаем просроченные рассылки
        now = timezone.now()
        Sending.objects.filter(
            owner=self.request.user,
            status='started',
            end_datetime__lt=now
        ).update(status='completed')

        return Sending.objects.filter(owner=self.request.user).select_related("message")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class SendingCreateView(LoginRequiredMixin, CreateView):
    """Создание новой рассылки"""
    model = Sending
    form_class = SendingForm
    template_name = "mailservices/sending_form.html"
    success_url = reverse_lazy('mailservices:sending_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ограничиваем выбор только объектами пользователя
        form.fields["message"].queryset = Message.objects.filter(owner=self.request.user)
        form.fields["recipients"].queryset = Client.objects.filter(owner=self.request.user)
        return form

class SendingDetailView(LoginRequiredMixin, DetailView):
    """Просмотр информации рассылки"""
    model = Sending
    # context_object_name = "sending"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = self.object.message
        return context


class SendingUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление информации рассылки"""
    model = Sending
    form_class = SendingForm
    template_name = "mailservices/sending_form.html"
    success_url = reverse_lazy('mailservices:sending_list')


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["message"].queryset = Message.objects.filter(owner=self.request.user)
        form.fields["recipients"].queryset = Client.objects.filter(owner=self.request.user)
        return form


class SendingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление конкретной рассылки"""
    model = Sending
    template_name = "mailservices/sending_confirm_delete.html"
    success_url = reverse_lazy('mailservices:sending_list')

class SendingNowView(View):
    """
    Вьюха для ручной отправки рассылки по кнопке.
    Доступна только владельцу.
    """

    def post(self, request, pk):
        sending = get_object_or_404(Sending, pk=pk)

        # Проверка владельца
        if sending.owner != request.user:
            messages.error(request, "Вы не можете отправить чужую рассылку.")
            return redirect('mailservices:sending_list')

        # Запускаем отправку
        send_mailing(sending)

        messages.success(request, f"Рассылка '{sending}' была обработана.")
        return redirect('mailservices:sending_list')
#################################################################################################

class AttemptListView(LoginRequiredMixin, ListView):
    model = MailAttempt
    template_name = 'mailservices/attempt_list.html'
    context_object_name = 'attempts'
    paginate_by = 10

    def test_func(self):
        """Разрешаем: админ, модератор, владелец"""
        user = self.request.user
        return user.is_superuser or hasattr(user, 'is_moderator') and user.is_moderator or user.is_authenticated

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return MailAttempt.objects.all().select_related('mailing', 'mailing__owner')

        if hasattr(user, 'is_moderator') and user.is_moderator:
            return MailAttempt.objects.all().select_related('mailing', 'mailing__owner')

        # Обычный пользователь — только свои попытки
        return MailAttempt.objects.filter(mailing__owner=user).select_related('mailing')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'История отправки писем'
        return context
#############################################################################################
"""Администрирование - для просмотра информации пользователей"""
class UserClientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Client
    template_name = 'mailservices/client_list.html'
    context_object_name = 'clients'  # теперь в шаблоне: {{ clients }}

    def test_func(self):
        """Разрешаем доступ, если есть право просмотра всех клиентов"""
        return self.request.user.has_perm('mailservices.can_view_all_clients')

    def get_queryset(self):
        # Получаем ID пользователя из URL
        user_id = self.kwargs['user_id']
        # Находим владельца
        self.owner = get_object_or_404(User, pk=user_id)
        # Возвращаем клиентов этого владельца
        return Client.objects.filter(owner=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner  # теперь self.owner определён
        return context


class UserMessageListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Message
    template_name = 'mailservices/message_list.html'
    context_object_name = 'messages'

    def test_func(self):
        return self.request.user.has_perm('mailservices.can_view_all_messages')

    def get_queryset(self):
        # Получаем ID пользователя из URL
        user_id = self.kwargs['user_id']
        # Находим владельца
        self.owner = get_object_or_404(User, pk=user_id)
        # Возвращаем клиентов этого владельца
        return Message.objects.filter(owner=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner  # теперь self.owner определён
        return context


class UserSendingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Sending
    template_name = 'mailservices/sending_list.html'
    context_object_name = 'sendings'

    def test_func(self):
        return self.request.user.has_perm('mailservices.can_view_all_sendings')

    def get_queryset(self):
        # Получаем ID пользователя из URL
        user_id = self.kwargs['user_id']
        # Находим владельца
        self.owner = get_object_or_404(User, pk=user_id)
        # Возвращаем клиентов этого владельца
        return Sending.objects.filter(owner=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner  # теперь self.owner определён
        context['now'] = timezone.now()# Для корректного отображения кнопки "Отпаравить" в шаблоне по времени
        return context

@login_required
def toggle_user_block_sending(request, pk):
    """Блокировка рассылки пользователя админом или модератором"""
    sending = get_object_or_404(Sending, pk=pk)

    # ✅ Переключаем статус
    sending.status = "completed"
    sending.save()

    return redirect('mailservices:sending_list')
