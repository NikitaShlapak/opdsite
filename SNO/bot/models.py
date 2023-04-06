import datetime

from django.contrib.auth.models import User
from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название', default='')
    publishing_time = models.DateTimeField('Дата оглашения', auto_now_add=True)
    act_time = models.DateTimeField('Дата прохождения')
    deadline = models.DateTimeField('Окончание приёма заявок')
    description = models.TextField('Описание')
    manager = models.ForeignKey(User, verbose_name='Ответственный', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/bot_files/%Y/%m/%d/', blank=True, verbose_name='Прилагаемый файл')

    def __str__(self):
        return f"{self.title} - {self.deadline.date()}"


    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

class Application(models.Model):
    user_id = models.CharField(max_length=20, verbose_name='id пользователя')
    data = models.CharField(max_length=100, verbose_name='Данные (ФИО, группа)', null=True)
    time = models.DateTimeField('Время подачи', auto_now_add=True)
    event = models.ForeignKey(Event, verbose_name='Событие', on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.data} - {self.event}"


    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

