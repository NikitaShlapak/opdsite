import random
import re
from datetime import datetime

from django.contrib.auth.models import AbstractUser

from django.db import models
from django.urls import reverse

from user_accounts.models import CustomUser, StudyGroup


class Project(models.Model):
    name_of_project = models.CharField('Название проекта', max_length=50)
    # date_create = models.DateTimeField('Дата публикации', auto_now_add=True)
    edition_key = models.PositiveSmallIntegerField(default=random.randint(1000,32000))

    class ProjectType(models.TextChoices):
        EXTERNAL = 'external', 'Внешний проект'
        SERVICE = 'service', 'Сервисный проект'
        RESEARCH = 'research', 'Исследовательский проект'

    project_type = models.CharField('Тип проекта',max_length=100, choices=ProjectType.choices)
    manager = models.ForeignKey(CustomUser, verbose_name='Руководитель проекта', on_delete=models.CASCADE,
                                max_length=50, related_name='manager',
                                limit_choices_to={'is_Free': True})

    target_groups = models.ManyToManyField(StudyGroup, verbose_name='Учебные группы исполнителей')


    class ImplementationPeriod(models.TextChoices):
        ONESEMESTR = 'One', 'На один семестр'
        TWOSEMESTRS = 'Two', 'На два семестра'
        TREESEMESTRS = 'Tree', 'На три семестра'
        MORESEMESTRS = 'More', 'На большее количество семестров'

    implementation_period = models.CharField(verbose_name='Срок реализации',max_length=50, choices=ImplementationPeriod.choices)

    class ProjectStatus(models.TextChoices):
        ENROLLMENTOPENED = 'opened', 'Набор открыт'
        ENROLLMENTCLOSED = 'closed', 'Набор закрыт'
        UNDERREVIEW = 'under_review', 'Проект на рассмотрении'
        REJECTED = 'rejected', 'Проект отклонён'

    project_status = models.CharField(max_length=15, choices=ProjectStatus.choices, default=ProjectStatus.UNDERREVIEW, verbose_name='Статус проекта' )
    team = models.ManyToManyField(CustomUser, verbose_name='Команда', null=True)

    short_project_description = models.CharField('Краткое описание проекта', max_length=150)
    long_project_description = models.TextField('Полное описание проекта')
    poster = models.ImageField(upload_to='uploads/img/%Y/%m/%d/', verbose_name='Постер')

    def __str__(self):
        return self.name_of_project

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.pk})

    def is_approved(self):
        return self.manager.is_approved or self.manager.is_staff

    def get_all_target_group_types(self):
        res = []
        for gr in self.target_groups.all():
            if not gr.type in res:
                res.append(gr.type)
        return ', '.join(res)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class Applications(models.Model):
    user =  models.ForeignKey(CustomUser, verbose_name='Пользователь', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}'s application to {self.project.name_of_project}"

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class ProjectReport(models.Model):
    heading = models.CharField(max_length=100, verbose_name='Заголовок', default='')
    publishing_time = models.DateTimeField('Дата публикации', auto_now_add=True)
    text = models.TextField('Текст')
    parent_project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/files/%Y/%m/%d/', blank=True, verbose_name='Прилагаемый файл')

    author = models.ForeignKey(CustomUser, verbose_name='Автор', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.parent_project}/{self.heading}"

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.parent_project.pk})


    def get_file_content_type(self):
        # print(self.file,type(self.file))
        res = re.sub(r"uploads/files/\d{4}/\d{2}/\d{2}/",'', self.file.name, count=1, flags=0)
        return res
    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'

