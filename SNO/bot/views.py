from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView

from .models import Event


class BotManageView(ListView):
    template_name = 'bot/bot_index.html'
    model = Event
    context_object_name = 'events'
    paginate_by = 12


class BotProfileView(LoginRequiredMixin ,TemplateView):
    template_name = 'bot/profile.html'

    def handle_no_permission(self):
        return redirect('user_accounts:login')

