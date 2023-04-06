from django.shortcuts import render
from django.views.generic import TemplateView



class BotManageView(TemplateView):
    template_name = 'bot/bot_index.html'

    #Bot = SNO_VK_BOT()
