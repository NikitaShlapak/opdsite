from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path('index/', views.BotManageView.as_view(), name='main'),
    path('home/', views.BotProfileView.as_view(), name='home'),
]