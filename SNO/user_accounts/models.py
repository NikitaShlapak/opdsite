from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models




class StudyGroup(models.Model):
    related_teacher = models.ForeignKey('CustomUser', verbose_name='Преподаватель', on_delete=models.SET_NULL, null=True)

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
        TEACHER = 'Преподаватель', 'Преподаватель'
        OUTSIDER = 'Внешний менеджер', 'Внешний менеджер'

    type = models.CharField(max_length=50, verbose_name='Тип группы',choices=StudyGroupType.choices, default=StudyGroupType.TEACHER)

    year = models.SmallIntegerField(verbose_name='год поступления', default=datetime.today().year)
    subgroup = models.SmallIntegerField(default=0, verbose_name='Подгруппа')

    def __str__(self):
        study_type = {
            'bachelors': ['БИЗ', 'БИО', 'ИВТ', 'ИС', 'М', 'МЕН', 'МТМ', 'МФ', 'ТД', 'ТФ', 'ХИМ', 'ХФМ', 'ЭКН', 'ЯФТ',
                          'ЯЭТ'],
            'specialists': ['АЭС', 'ЛД', 'ЭиА', 'ЯРМ'],
        }
        ans = self.type

        if ans in study_type['bachelors']:
            if self.subgroup:
                ans = ans + f"{self.subgroup}-Б{self.year%1000}"
            else:
                ans = ans + f"-Б{self.year%1000}"
        elif ans in study_type['specialists']:
            if self.subgroup:
                ans = ans + f"{self.subgroup}-C{self.year%1000}"
            else:
                ans = ans + f"-C{self.year%1000}"
        return ans
    class Meta:
        verbose_name = 'Учебная группа'
        verbose_name_plural = 'Учебные группы'


class CustomUser(AbstractUser):

    username = models.CharField(max_length=50, verbose_name='Имя пользователя', unique=True,
                                error_messages={'unique': "Пользователь с таким именем уже зарегистрирован!"})
    password = models.CharField(max_length=255, verbose_name='Пароль')
    email = models.EmailField(unique=False, verbose_name='Почта', #TODO: set 'unique' to TRUE for prod!
                              error_messages={'unique': "К этой почте уже привязана учётная запись!"})
    registration_time = models.DateTimeField('Дата регистрации', auto_now_add=True)

    study_group = models.ForeignKey(StudyGroup,verbose_name='Учебная группа', null=True, on_delete=models.SET_NULL, blank=True)
    is_approved = models.BooleanField(default=False)
    is_Free = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.study_group})"