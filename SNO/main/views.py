from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DetailView
from django.contrib.auth import logout as django_logout

from .models import *
from .forms import *
from .utils import *
from SNO.env import EMAIL_HOST_USER


def page_not_found_view(request, exception):
    data = {
        'group_form': SearchForm(),
        'exeption': exception
    }
    return render(request,'404.html', context=data)

def Main(request):
    projects = Project.objects.all().order_by('-id')

    if request.GET:
        if 'group' in request.GET:
            group_form = SearchForm({'group': request.GET['group']})
            projects = find_by_group(all_projects=projects, group=request.GET['group'])
        else:
            group_form = SearchForm()

        if 'name' in request.GET:
            name_form = SearchNameForm({'name': request.GET['name']})
            projects = find_by_name(data=request.GET['name'])
        else:
            name_form = SearchNameForm()
    else:
        group_form = SearchForm()
        name_form = SearchNameForm()

    if len(projects) > 0:
        text = f'Найдено проектов: {len(projects)}'
    else:
        text = 'Проектов по запросу не найдено'

    data = {
        'projects': projects,
        'selected': 'all',
        'group_form': group_form,
        'text': text,
        'name_form': name_form,
    }
    data['title']= form_title(data['selected'])

    return render(request, 'main/index.html', context=data)


def Info(request):
    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'selected': 'info'
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/info.html', context=data)


def MainFiltered(request, type):
    if type in Project.ProjectStatus:
        projects = Project.objects.filter(project_status=type).order_by('-id')

    elif type in Project.ProjectType:
        projects = Project.objects.filter(project_type=type).order_by('-id')
    if request.GET:
        if 'group' in request.GET:
            group_form = SearchForm({'group': request.GET['group']})
            projects = find_by_group(all_projects=projects, group=request.GET['group'])
        else:
            group_form = SearchForm()
    else:
        group_form = SearchForm()

    name_form = SearchNameForm()

    if len(projects) > 0:
        text = f'Найдено проектов: {len(projects)}'
    else:
        text = 'Проектов по запросу не найдено'

    data = {
        'projects': projects,
        'selected': type,
        'group_form': group_form,
        'text': text,
        'name_form': name_form,
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/index.html', context=data)


def Opd(request):
    return render(request, 'opd/index.html')


def ProjectPage(request, project_id):
    project = Project.objects.get(pk=project_id)
    # get_object_or_404(project)
    team = project.team.all()
    group_form = SearchForm()
    reject_form = ProjectRejectForm()
    data = {
        'reject_form': reject_form,
        'group_form': group_form,
        'p': project,
        'team': team,
        'selected': project.project_type,
        'verification_form':ProjectConfirmationForm(),
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/project_page.html', data)


def AddReport(request, project_id):
    project = Project.objects.get(pk=project_id)
    get_object_or_404(project)
    team = CustomUser.objects.filter(current_project=project_id)

    if request.method == 'POST':
        form = ProjectReportForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['author'] in team:
                data = form.cleaned_data
                data['parent_project'] = project
                try:
                    ProjectReport.objects.create(**data)
                    return redirect('project', project.pk)
                except:
                    form.add_error(None, 'Ошибка добавления отчёта')
            else:
                form.add_error(None,
                               'Указанный участник не может быть автором отчёта, так как не состоит в команде проекта!')
    else:
        form = ProjectReportForm()

    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'p': project,
        'team': team,
        'selected': project.project_type,
        'form': form

    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/add_coment.html', data)


def AddProject(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            if len(form.cleaned_data['long_project_description']) > len(form.cleaned_data['short_project_description']):
                if (form.cleaned_data['manager'].current_project):
                    form.add_error(None,
                                   'Этот студент не может быть менеджером проекта, так как уже подал заявку в другой '
                                   'или является менеджером')
                else:
                    try:
                        pr = Project.objects.create(edition_key=generate_edition_key(),**form.cleaned_data)
                        form.cleaned_data['manager'].current_project = pr
                        form.cleaned_data['manager'].is_free = False
                        form.cleaned_data['manager'].save()
                        return redirect('MAIN')
                    except:
                        form.add_error(None, 'Ошибка регистрации проекта')
            else:
                form.add_error(None, 'Длинное описание проекта не может быть короче краткого!')
    else:
        form = ProjectForm()
    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'selected': 'add',
        'form': form
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/add_project.html', context=data)


def AddTeamMember(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            try:
                CustomUser.objects.create(**form.cleaned_data)
                send_mail(
                    'Регистрация',
                    'Вы успешно зарегистрированы на портале iate.projects!',
                    EMAIL_HOST_USER,
                    [form.cleaned_data['email']],
                    fail_silently=True,
                )
                return redirect('MAIN')
            except:
                form.add_error(None, 'Ошибка регистрации пользователя')
    else:
        form = TeamMemberForm()
    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'selected': 'reg',
        'url': 'add_user',
        'form': form
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/add_user.html', context=data)


def confirm_app(request, student_id, project_id):
    student = CustomUser.objects.get(pk=student_id)
    project = Project.objects.get(pk=project_id)
    if student.current_project.pk == project_id:
        try:

            student.is_free = False
            student.save()
            send_mail(
                'Изменение статуса участника',
                f"Ваш статус в проекте {project.name_of_project} изменён: вы приняты в команду.",
                EMAIL_HOST_USER,
                [student.email],
                fail_silently=True,
            )
        except:
            return HttpResponse('Ошибка изменения базы данных')
    else:
        return HttpResponse('Студент не подавал заявки на этот проект или её состояние уже изменено')
    return redirect('project', project_id=project_id)


def decline_app(request, student_id, project_id):
    student = CustomUser.objects.get(pk=student_id)
    project = Project.objects.get(pk=project_id)
    if student.current_project.pk == project_id:
        try:
            student.save()
            send_mail(
                'Изменение статуса участника',
                f"Ваш статус в проекте {project.name_of_project} изменён: ваша заявка отклонена менеджером.",
                EMAIL_HOST_USER,
                [student.email],
                fail_silently=True,
            )
        except:
            return HttpResponse('Ошибка изменения базы данных')
    else:
        return HttpResponse('Студент не подавал заявки на этот проект или её состояние уже изменено')
    return redirect('project', project_id=project_id)


def ExpandTeam(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.method == 'POST':
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                data['current_project'] = project
                data['state'] = CustomUser.State.OBSERVED
                student = CustomUser.objects.create(**data)
                send_mail(
                    'Заявка на проект подана успешно',
                    f"Вы успешно подали заявку на проект {project.name_of_project}. Вы получите уведомление о её принятии или отклонении менеджером.",
                    EMAIL_HOST_USER,
                    [data['email']],
                    fail_silently=True,
                )
                msg = f'''На ваш проект {project.name_of_project} подали заявку.
                        Информация о студенте:
                        {data['secondname']} {data['firstname']}, группа {data['group']}.
                        Перейдите по соотвествующей ссылке, чтобы принять или отклонить заявку:
                        Принять - http://opd.iate.obninsk.ru/project/{project.pk}/{student.pk}/apply
                        Отклонить - http://opd.iate.obninsk.ru/project/{project.pk}/{student.pk}/decline
                        Почта для связи: {data['email']}'''
                send_mail(
                    f'Заявки | {project.name_of_project}',
                    msg,
                    EMAIL_HOST_USER,
                    [project.manager_email],
                    fail_silently=False,
                )
                return render(request, 'main/reg_success.html')
            except:
                form.add_error(None, 'Ошибка регистрации пользователя')
    else:
        form = TeamMemberForm()
    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'p': project,
        'url': 'expand',
        'selected': 'reg',
        'form': form
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/add_user.html', context=data)

def verify_edition(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.method == 'POST':
        form = ProjectConfirmationForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['edition_key']
            # print(form.cleaned_data)
            if key == project.edition_key:
                # print('OK')
                return redirect('edit', pk=project.pk, edition_key=key)
            else:
                form.add_error(None, 'Код неверен')

    else:
        form = ProjectConfirmationForm()
    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'p': project,
        'url': 'edit',
        'selected': 'add',
        'form': form
    }
    return render(request, 'main/edit_project.html', context=data)


def reject_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.method == 'POST':
        form = ProjectRejectForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['edition_key']
            # print(form.cleaned_data)
            if key == project.edition_key:
                print('OK')
                print(form.cleaned_data)

                msg = f'''Ваш проект "{project.name_of_project}" был отклонён пользователем {request.user}.
                                        Причина:
                                        {form.cleaned_data['reason']} 
                                        Комментарий:
                                        {form.cleaned_data['comment']} 
                                        Перейдите по ссылке, чтобы отредактировать заявку:
                                        http://opd.iate.obninsk.ru/project/{project.pk}/edit/{key}
                                        '''
                send_mail(
                    f'Заявки | {project.name_of_project}',
                    msg,
                    EMAIL_HOST_USER,
                    [project.manager_email],
                    fail_silently=False,
                )

                project.project_status = project.ProjectStatus.REJECTED
                project.save()

                return redirect('project', pk=project.pk)
            else:
                form.add_error(None, 'Код неверен')

    else:
        form = ProjectRejectForm()
    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'p': project,
        'url': 'edit',
        'selected': 'add',
        'form': form
    }
    return render(request, 'main/edit_project.html', context=data)



class ProjectUpdateView(UpdateView):
    model = Project
    template_name = "main/edit_project.html"

    form_class = ProjectEditForm

    def get_context_data(self):
        context = super(ProjectUpdateView, self).get_context_data()| self.kwargs
        return context


class RegisterUser(DataMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = "main/register+login.html"
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='register')
        return context|c_def


class LoginUser(DataMixin, LoginView):
    form_class = CustomUserAuthenticationForm
    template_name = 'main/register+login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='login')
        return context|c_def
    # def get_success_url(self):
    #     return reverse_lazy('MAIN')

def logout(request):
    django_logout(request)
    return redirect('login')

# class ProfilePage(DataMixin, DetailView):