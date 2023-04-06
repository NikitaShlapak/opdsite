from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.BotManageView.as_view(), name='bot_index'),
]