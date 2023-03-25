import random
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse




class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, verbose_name='Имя пользователя', unique=True,
                                error_messages={'unique': "Пользователь с таким именем уже "
                                                          "зарегистрирован"})
    password = models.CharField(max_length=255, verbose_name='Пароль')
    email = models.EmailField(unique=False, verbose_name='Почта')


    registration_time = models.DateTimeField('Дата регистрации', auto_now_add=True)

    regex = r'([а-яА-ЯёЁ]{1,4}\d?-[1-9а-яА-ЯёЁ]{1,4}\d?)|Преподаватель' # 1-4 буквы, затем '-' и 1-4 цифры/буквы ИЛИ "Преподаватель"
    study_group = models.CharField('Группа', max_length=15, blank=True,null=True,default='Преподаватель',
                             validators=[RegexValidator(regex=regex, message='Некорректное название группы')])

    is_approved = models.BooleanField(default=False)
    is_Free = models.BooleanField(default=True)




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
    team = models.ManyToManyField(CustomUser, verbose_name='Команда', null=True)
    # applies = models.ManyToManyField(CustomUser, verbose_name='Заявки', null=True)
    short_project_description = models.CharField('Краткое описание проекта', max_length=150)
    long_project_description = models.TextField('Полное описание проекта')
    poster = models.ImageField(upload_to='uploads/img/%Y/%m/%d/', verbose_name='Постер')

    def __str__(self):
        return self.name_of_project

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.pk})



    def is_approved(self):
        return self.manager.is_approved

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'





class ProjectReport(models.Model):
    heading = models.CharField(max_length=100, verbose_name='Заголовок', default='')
    # publishing_time = models.DateTimeField('Дата публикации', auto_now_add=True)
    text = models.TextField('Текст')
    parent_project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/files/%Y/%m/%d/', blank=True, verbose_name='Прилагаемый файл')

    author = models.ForeignKey(CustomUser, verbose_name='Автор', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.parent_project}/{self.heading}"

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.parent_project.pk})

    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'


class StudyGroup(models.Model):

    class StudyGroupType(models.TextChoices):
        AES = 'АЭС', 'АЭС'
        EIA = 'ЭиА', 'ЭиА'
        YARM = 'ЯРМ', 'ЯРМ'
        BIZ = 'БИЗ', 'БИЗ'
        BIO = 'БИО', 'БИО'
        IVT = 'ИВТ', 'ИВТ'
        IS = 'ИС', 'ИС'
        M = 'М', 'М'
        MEN = 'МЕН', 'МЕН'
        MTM = 'МТМ', 'МТМ'
        MF = 'МФ', 'МФ'
        TD = 'ТД', 'ТД'
        TF = 'ТФ', 'ТФ'
        HIM = 'ХИМ', 'ХИМ'
        HFM = 'ХФМ', 'ХФМ'
        EKN = 'ЭКН', 'ЭКН'
        YAFT = 'ЯФТ', 'ЯФТ'
        YAET = 'ЯЭТ', 'ЯЭТ'

    type = models.CharField(max_length=5, verbose_name='Тип группы',choices=StudyGroupType.choices)

    class Years(models.TextChoices):
        FIRST  = "1", "Первый"
        SECOND = "2", "Второй"

    year = models.CharField(max_length=2, verbose_name='Курс',choices=Years.choices)
    subgroup = models.SmallIntegerField(default=0, verbose_name='Подгруппа')

    def __str__(self):
        study_type = {
            'bachelors': ['БИЗ', 'БИО', 'ИВТ', 'ИС', 'М', 'МЕН', 'МТМ', 'МФ', 'ТД', 'ТФ', 'ХИМ', 'ХФМ', 'ЭКН', 'ЯФТ',
                          'ЯЭТ'],
            'specialists': ['АЭС', 'ЛД', 'ЭиА', 'ЯРМ'],
        }
        ans = self.type
        current_date = datetime.today()
        if current_date.month < 9: #Январь-август (1-8 месяцы) - весенний семестр
            if self.year == self.Years.FIRST:
                app = str(current_date.year - 1)[-2:]
            elif self.year == self.Years.SECOND:
                app = str(current_date.year - 2)[-2:]
        else: #Осенний семестр
            if self.year == self.Years.FIRST:
                app = str(current_date.year)[-2:]
            elif self.year == self.Years.SECOND:
                app = str(current_date.year - 1)[-2:]

        if ans in study_type['bachelors']:
            if self.subgroup:
                ans = ans + f"{self.subgroup}-Б{app}"
            else:
                ans = ans + f"-Б{app}"
        elif ans in study_type['specialists']:
            if self.subgroup:
                ans = ans + f"{self.subgroup}-C{app}"
            else:
                ans = ans + f"-C{app}"
        return ans
    class Meta:
        verbose_name = 'Учебная группа'
        verbose_name_plural = 'Учебные группы'