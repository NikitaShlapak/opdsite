import random
import re
from django.db import models
from django.db.models import Q
from django.urls import reverse


from main.standalone_utils import WikiPlainHTMLTextTransformer
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
                                max_length=50, related_name='manager')

    target_groups = models.ManyToManyField(StudyGroup, verbose_name='Учебные группы исполнителей',limit_choices_to=~Q(type__in=[StudyGroup.StudyGroupType.TEACHER,StudyGroup.StudyGroupType.OUTSIDER]))


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
    team = models.ManyToManyField(CustomUser, verbose_name='Команда', blank=True)

    short_project_description = models.CharField('Краткое описание проекта', max_length=150)
    long_project_description = models.TextField('Полное описание проекта')
    poster = models.ImageField(upload_to='uploads/img/%Y/%m/%d/', verbose_name='Постер')

    def __str__(self):
        return self.name_of_project

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.pk})
    def get_html_desc(self):
        conv = WikiPlainHTMLTextTransformer()
        return conv.fit(self.long_project_description)
    def is_approved(self):
        return self.manager.is_approved or self.manager.is_staff

    def get_all_target_group_types(self):
        res = []
        for gr in self.target_groups.all():
            if not gr.type in res:
                res.append(gr.type)
        return ', '.join(res)

    def get_all_target_group_types_list(self):
        res = []
        for gr in self.target_groups.all():
            if not gr.type in res:
                res.append(gr.type)
        return res

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
        return f"{self.parent_project} - {self.heading}"

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.parent_project.pk})
    def get_html_text(self):
        conv = WikiPlainHTMLTextTransformer()
        return conv.fit(self.text)
    def is_markable(self):
        if not (self.author.study_group.type == StudyGroup.StudyGroupType.TEACHER or self.author.study_group.type == StudyGroup.StudyGroupType.OUTSIDER):
            return True
        else:
            return False
            # return f"{self.author.study_group.type} - {StudyGroup.StudyGroupType.TEACHER} - {self.author.study_group.type == StudyGroup.StudyGroupType.TEACHER}"

    def get_average_mark(self):
        average_mark = 0
        if self.is_markable():
            all_marks = self.projectreportmark_set.all()
            if len(all_marks) > 0:
                for mark in all_marks:
                    average_mark = average_mark + mark.value/len(all_marks)
        return average_mark

    def get_file_content_type(self):
        # print(self.file,type(self.file))
        res = re.sub(r"uploads/files/\d{4}/\d{2}/\d{2}/",'', self.file.name, count=1, flags=0)
        return res
    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'

class ProjectReportMark(models.Model):
    related_report = models.ForeignKey(ProjectReport, verbose_name='Отчёт', on_delete=models.CASCADE)
    author=models.ForeignKey(CustomUser, verbose_name='Преподаватель',
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         limit_choices_to={'study_group__type':StudyGroup.StudyGroupType.TEACHER})
    creation_time = models.DateTimeField('Дата', auto_now_add=True)
    comment = models.CharField(max_length=250,verbose_name='Комментарий', null=True, blank=True)
    value = models.SmallIntegerField(verbose_name='Балл')

    def __str__(self):
        return f"Оценка пользователя {self.author.username} к отчёту {self.related_report}."

    def get_absolute_url(self):
        return self.related_report.get_absolute_url()
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

