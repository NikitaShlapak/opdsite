# Generated by Django 4.1.1 on 2022-09-21 19:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_of_project', models.CharField(max_length=50, verbose_name='Name_of_project')),
                ('project_type', models.CharField(choices=[('E', 'Внешний проект'), ('S', 'Сервисный проект'), ('R', 'Исследовательский проект')], max_length=1)),
                ('target_groups', models.CharField(max_length=50, verbose_name='Целевые группы')),
                ('manager_email', models.EmailField(max_length=50, verbose_name='Email руководителя')),
                ('implementation_period', models.CharField(choices=[('One', 'На один семестр'), ('Two', 'На два семестра'), ('Tree', 'На три семестра'), ('More', 'На большее количество семестров')], max_length=5)),
                ('project_status', models.CharField(choices=[('OPEN', 'Набор открыт'), ('CLOSE', 'Набор закрыт'), ('UR', 'Проект на рассмотрении'), ('REJ', 'Проект отклонён')], default='UR', max_length=5)),
                ('short_project_description', models.CharField(max_length=50, verbose_name='Краткое описание проекта')),
                ('long_project_description', models.TextField(max_length=50, verbose_name='Длинное описание проекта')),
                ('poster', models.ImageField(max_length=50, upload_to='templates/uploads/img/', verbose_name='Постер')),
            ],
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='Email')),
                ('secondname', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('firstname', models.CharField(max_length=50, verbose_name='Имя')),
                ('group', models.CharField(blank=True, max_length=10, verbose_name='Группа')),
                ('state', models.CharField(choices=[('Подтверждён', 'Участник в команде'), ('Отклонён', 'Участник не в команде'), ('На рассмотрении', 'Заявка рассматривается')], default='На рассмотрении', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publishing_time', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('text', models.TextField(verbose_name='Текст')),
                ('file', models.FileField(upload_to='templates/uploads/files/')),
                ('author', models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.CASCADE, to='main.teammember', verbose_name='Автор проекта')),
                ('parent_project', models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.CASCADE, to='main.project', verbose_name='Проект родитель')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='manager',
            field=models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.CASCADE, related_name='manger', to='main.teammember', verbose_name='Руководитель проекта'),
        ),
        migrations.AddField(
            model_name='project',
            name='team',
            field=models.ManyToManyField(to='main.teammember', verbose_name='Команда'),
        ),
    ]
