import random

from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse


class TeamMember(models.Model):
    email = models.EmailField('Email', null=True, unique=False, max_length=100)
    secondname = models.CharField('Фамилия', max_length=50, blank=False)
    firstname = models.CharField('Имя', max_length=50, blank=False)
    regex = r'([а-яА-ЯёЁ]{1,4}\d?-[1-9а-яА-ЯёЁ]{1,4}\d?)|Преподаватель'
    group = models.CharField('Группа', max_length=15, blank=True, validators=[RegexValidator(regex=regex, message='Некорректное название группы')])
    current_project = models.ForeignKey('Project', verbose_name='Проект студента', on_delete=models.CASCADE,
                                        max_length=50, null=True, blank=True)

    class State(models.TextChoices):
        TEACHER = 'Преподаватель', 'Сотрудник ИАТЭ'
        MANAGER = 'Куратор', 'Менеджер проекта'
        APPLIED = 'Подтверждён', 'Участник в команде'
        REJECTED = 'Отклонён', 'Участник не в команде'
        OBSERVED = 'На рассмотрении', 'Заявка рассматривается'
        UNDEFINED = 'Не подан', 'Заявка не подана'

    state = models.CharField(max_length=20, choices=State.choices, default=State.UNDEFINED, blank=False)
    is_approved = models.BooleanField(default=False)
    is_Free = models.BooleanField(default=True)

    REQUIRED_FIELDS = [email, firstname, secondname]

    def __str__(self):
        return f"{self.firstname} {self.secondname} ({self.group})"

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.current_project.pk})+'#team'

    def get_full_name(self):
        return self.firstname + ' ' + self.secondname

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


class Project(models.Model):
    name_of_project = models.CharField('Название проекта', max_length=50)
    date_create = models.DateTimeField(auto_now_add=True, blank=True)
    edition_key = models.PositiveSmallIntegerField(default=1000)

    class ProjectType(models.TextChoices):
        EXTERNAL = 'external', 'Внешний проект'
        SERVICE = 'service', 'Сервисный проект'
        RESEARCH = 'research', 'Исследовательский проект'

    project_type = models.CharField('Тип проекта',max_length=100, choices=ProjectType.choices)
    manager = models.ForeignKey(TeamMember, verbose_name='Руководитель проекта', on_delete=models.CASCADE,
                                max_length=50, related_name='manager',
                                limit_choices_to={'is_Free': True})
    target_groups = models.CharField('Целевые группы', max_length=100)
    manager_email = models.EmailField('Email руководителя', blank=False)

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
    # team = models.ManyToManyField(TeamMember, verbose_name='Команда')
    short_project_description = models.CharField('Краткое описание проекта', max_length=150)
    long_project_description = models.TextField('Полное описание проекта')
    poster = models.ImageField(upload_to='uploads/img/%Y/%m/%d/', verbose_name='Постер')

    def __str__(self):
        return self.name_of_project

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.pk})

    def get_team(self):
        return TeamMember.objects.filter(current_project=self.pk)

    def is_approved(self):
        return self.manager.is_approved

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class ProjectReport(models.Model):
    heading = models.CharField(max_length=100, verbose_name='Заголовок', default='')
    publishing_time = models.DateTimeField('Дата публикации', auto_now_add=True)
    text = models.TextField('Текст')
    parent_project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/files/%Y/%m/%d/', blank=True, verbose_name='Прилагаемый файл')

    author = models.ForeignKey(TeamMember, verbose_name='Автор', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.parent_project}/{self.publishing_time}/{self.heading}"

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.parent_project.pk})

    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'
