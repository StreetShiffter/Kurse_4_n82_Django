
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy

from .forms import ClientForm, MessageForm
from .models import Sending, Message, Client


def home_view(request):
    '''Отображение статистики рассылки'''
    total_mailings = Sending.objects.filter(owner=request.user).count()
    active_mailings = Sending.objects.filter(owner=request.user, status="started").count()
    unique_recipients = Client.objects.filter(owner=request.user).values('email').distinct().count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
    }
    return render(request, "mailservices/home.html", context)

##########################################################################################

# Client CRUD
class ClientCreateView(CreateView):
    """Создание записи о клиенте"""
    model = Client
    form_class = ClientForm
    template_name = "mailservices/client_form.html"
    success_url = reverse_lazy("mailservices:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientDetailView(DetailView):
    """Просмотр записи о клиенте"""
    model = Client
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ClientUpdateView(UpdateView):
    """Редактирование записи клиента"""
    model = Client
    form_class = ClientForm
    template_name = "mailservices/client_form.html"
    success_url = reverse_lazy("mailservices:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientListView(ListView):
    model = Client
    template_name = "mailservices/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailservices/client_confirm_delete.html"
    success_url = reverse_lazy('mailservices:client_list')

#################################################################################

# Message CRUD
class MessageCreateView(CreateView):
    """Создание сообщения"""
    model = Message
    form_class = MessageForm
    template_name = "mailservices/message_form.html"
    success_url = reverse_lazy("mailservices:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MessageListView(ListView):
    """Просмотр всех сообщений"""
    model = Message
    template_name = "mailservices/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailservices/message_form.html"
    success_url = reverse_lazy("mailservices:message_list")

class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailservices/message_confirm_delete.html"
    success_url = reverse_lazy("mailservices:message_list")

class ClientDetailView(DetailView):
    """Просмотр записи о клиенте"""
    model = Client
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



# Mailing CRUD
class SendingListView(ListView):
    model = Sending
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return Sending.objects.filter(owner=self.request.user).select_related("message")


class SendingCreateView(CreateView):
    model = Sending
    fields = ["start_datetime", "end_datetime", "message", "recipients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ограничиваем выбор только объектами пользователя
        form.fields["message"].queryset = Message.objects.filter(owner=self.request.user)
        form.fields["recipients"].queryset = Client.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class SendingUpdateView(UpdateView):
    model = Client
    fields = ["start_datetime", "end_datetime", "message", "recipients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["message"].queryset = Message.objects.filter(owner=self.request.user)
        form.fields["recipients"].queryset = Client.objects.filter(owner=self.request.user)
        return form


class SendingDeleteView(DeleteView):
    model = Sending
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")

