from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

institutes_and_groups =[
    ['ТФ','ЯЭТ','ТД', 'Э','ЯФТ', 'МФ','МН', 'САУ','Р','УОС','РБ', 'АЭС','ЯРМ','ЯЭУ', 'ЭиА','ФКС', 'МТМ',  'ПМФ'],#ЯФиТ
    ['ХИМ','ЛД','БИО', 'ХФМ',  'ПМК' ],#ОБТ
    ['УСЭС','БИЗ','ЭКН','ГМУ'],#СЭН
    ['ИВТ', 'МЕН','ИС',  'АУТ','М' ],#ИИКС
]


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
        LD = 'ЛД', 'ЛД'
        TF = 'ТФ', 'ТФ'
        HIM = 'ХИМ', 'ХИМ'
        HFM = 'ХФМ', 'ХФМ'
        EKN = 'ЭКН', 'ЭКН'
        YAFT = 'ЯФТ', 'ЯФТ'
        YAET = 'ЯЭТ', 'ЯЭТ'
        TEACHER = 'Преподаватель', 'Преподаватель'
        OUTSIDER = 'Внешний менеджер', 'Внешний менеджер'
    class StudyGroupCourseType(models.TextChoices):
        SPEC = 'С', 'Специалитет'
        BACH = 'Б', 'Бакалавриат'
        MAG = 'М', 'Магистратура'
        ASP = 'А', 'Аспирантура'

        OTHER = '', 'Другое'
    class StudyGroupInstituteType(models.TextChoices):
        YaFIT = 'оЯФиТ', 'отделение ядерной физики и технологий'
        OBT = 'ОБТ', 'отделение биотехнологий'
        SEN = 'СЭН', 'социально-экономическое направление'
        IKS = 'ИИКС', 'институт интеллектуальных и кибернетических систем'

        OTHER = '', 'Другое'

    type = models.CharField(max_length=50, verbose_name='Тип группы', choices=StudyGroupType.choices,
                            default=StudyGroupType.OUTSIDER)
    institute = models.CharField(max_length=50, verbose_name='Отделение', choices=StudyGroupInstituteType.choices,
                              default=StudyGroupInstituteType.OTHER)
    year = models.SmallIntegerField(verbose_name='год поступления', default=datetime.today().year)
    subgroup = models.SmallIntegerField(default=0, verbose_name='Подгруппа')
    course = models.CharField(max_length=50, verbose_name='Программа обучения', choices=StudyGroupCourseType.choices,
                              default=StudyGroupCourseType.OTHER)
    numgroup = models.SmallIntegerField(default=0, verbose_name='Номер группы', help_text='оставьте 0, если такая группа на потоке единственная')
    timetable_id = models.IntegerField(default=111, verbose_name='id группы в расписании')
    is_foreigns = models.BooleanField(default=False, verbose_name='Иностранцы')

    def short_str(self):
        ans = self.type
        if not self.type in [self.StudyGroupType.OUTSIDER, self.StudyGroupType.TEACHER]:
            app_sub = ''
            app_num = ''
            app_type = f'-{self.course}{int(self.year) % 1000}'

            if self.numgroup:
                app_num = self.numgroup

            ans = ans + f"{app_num}{app_type}{app_sub}"
            if self.is_foreigns:
                ans = ans + 'и'
        return ans
    def __str__(self):
        ans = self.type
        if not self.type in [self.StudyGroupType.OUTSIDER, self.StudyGroupType.TEACHER]:
            app_sub=''
            app_num=''
            app_type = f'-{self.course}{int(self.year) % 1000}'

            if self.numgroup:
                app_num = self.numgroup

            ans = ans + f"{app_num}{app_type}{app_sub}"
            if self.is_foreigns:
                ans = ans+'и'
            if self.subgroup:
                ans = ans + f" (подгруппа {self.subgroup})"
        return ans

    def get_timetable_link(self):
        return f"http://timetable.iate.obninsk.ru/group/{self.timetable_id}"
    def set_institute(self):
        if   self.type in institutes_and_groups[0]:
            self.institute = self.StudyGroupInstituteType.YaFIT
        elif self.type in institutes_and_groups[1]:
            self.institute = self.StudyGroupInstituteType.OBT
        elif self.type in institutes_and_groups[2]:
            self.institute = self.StudyGroupInstituteType.SEN
        elif self.type in institutes_and_groups[3]:
            self.institute = self.StudyGroupInstituteType.IKS
        else:
            self.institute = self.StudyGroupInstituteType.OTHER

    def get_study_year(self):
        dif = datetime.today().year - self.year
        if 1< datetime.today().month<8:
            dif = dif+1
        return dif

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
    is_approved = models.BooleanField(default=False, verbose_name='Подтверждённый менеджер', help_text='Статус подтверждённого менеджера. Его проекты автоматически подтверждаются, а также выделяются особым значком в списке проектов.')
    is_Free = models.BooleanField(default=True)


    def __str__(self):
        if not self.get_full_name():
            return self.username
        return f"{self.get_full_name()} ({self.study_group})"

class VKTokenConnection(models.Model):

    email = models.EmailField(unique=False, verbose_name='Почта', #TODO: set 'unique' to TRUE for prod!
                              error_messages={'unique': "К этой почте уже привязана учётная запись!"})
    user_id = models.CharField(max_length=50, verbose_name='VK ID')
    access_token = models.TextField(verbose_name='Токен')
    expires_in = models.IntegerField(verbose_name='Время действия (в секундах)', help_text='Если 0, то токен бессрочный')
    dt_created = models.DateTimeField(verbose_name='Время создания', auto_now_add=True)

