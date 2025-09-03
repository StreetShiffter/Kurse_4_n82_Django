
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Sending, Message, Client


# Главная страница — отображение статистики

def home_view(request):
    total_mailings = Sending.objects.filter(owner=request.user).count()
    active_mailings = Sending.objects.filter(owner=request.user, status="started").count()
    unique_recipients = Client.objects.filter(owner=request.user).values('email').distinct().count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
    }
    return render(request, "mailservices/home.html", context)


# Recipient CRUD
class ClientListView(ListView):
    model = Client
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


class ClientCreateView(CreateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClienttUpdateView(UpdateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("recipient_list")


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("recipient_list")



# Message CRUD
class MessageListView(ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(CreateView):
    model = Message
    fields = ["mail_title", "mail_body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    fields = ["mail_title", "mail_body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("message_list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("message_list")



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
