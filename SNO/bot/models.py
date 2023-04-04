from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название', default='')
    publishing_time = models.DateTimeField('Дата оглашения', auto_now_add=True)
    act_time = models.DateTimeField('Дата прохождения')
    deadline = models.DateTimeField('Окончание приёма заявок')
    description = models.TextField('Описание')
    manager = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/files/%Y/%m/%d/', blank=True, verbose_name='Прилагаемый файл')

    # author = models.ForeignKey(TeamMember, verbose_name='Автор', on_delete=models.CASCADE)
    #
    # def __str__(self):
    #     return f"{self.parent_project}/{self.publishing_time}/{self.heading}"
    #
    # def get_absolute_url(self):
    #     return reverse('project', kwargs={'project_id': self.parent_project.pk})

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

