from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import UpdateView

from .models import *
from .forms import *
from .utils import *

def page_not_found_view(request, exception):
    data = {
        'group_form': SearchForm(),
        'exeption': exception
    }
    return render(request,'404.html', context=data)

def Main(request):
    projects = Project.objects.exclude(project_status=Project.ProjectStatus.REJECTED).order_by('-date_create')
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
        projects = Project.objects.filter(project_status=type).order_by('-date_create')

    elif type in Project.ProjectType:
        projects = Project.objects.filter(project_type=type).order_by('-date_create')
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
    team = TeamMember.objects.filter(current_project=project_id).order_by('state')
    group_form = SearchForm()
    reject_form = ProjectRejectForm()
    desc = project.long_project_description.split(sep='\n')
    data = {
        'reject_form': reject_form,
        'group_form': group_form,
        'p': project,
        'team': team,
        'selected': project.project_type,
        'verification_form':ProjectConfirmationForm(),
        'desc':desc
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/project_page.html', data)


def AddReport(request, project_id):
    project = Project.objects.get(pk=project_id)
    team = TeamMember.objects.filter(current_project=project_id)

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
                if (form.cleaned_data['manager'].current_project and
                        form.cleaned_data['manager'].state != TeamMember.State.TEACHER and
                        form.cleaned_data['manager'].state != TeamMember.State.REJECTED):
                    form.add_error(None,
                                   'Этот студент не может быть менеджером проекта, так как уже подал заявку в другой '
                                   'или является менеджером')
                else:
                    try:
                        pr = Project.objects.create(edition_key=generate_edition_key(),**form.cleaned_data)
                        form.cleaned_data['manager'].current_project = pr
                        if form.cleaned_data['manager'].state != TeamMember.State.TEACHER:
                            form.cleaned_data['manager'].state = TeamMember.State.MANAGER
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
                TeamMember.objects.create(**form.cleaned_data)
                send_mail(
                    'Регистрация',
                    'Вы успешно зарегистрированы на портале iate.projects!',
                    'nikitashlapak04@gmail.com',
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
    student = TeamMember.objects.get(pk=student_id)
    project = Project.objects.get(pk=project_id)
    if student.state == TeamMember.State.OBSERVED and student.current_project.pk == project_id:
        try:
            student.state = TeamMember.State.APPLIED
            student.is_free = False
            student.save()
            send_mail(
                'Изменение статуса участника',
                f"Ваш статус в проекте {project.name_of_project} изменён: вы приняты в команду.",
                'nikitashlapak04@gmail.com',
                [student.email],
                fail_silently=True,
            )
        except:
            return HttpResponse('Ошибка изменения базы данных')
    else:
        return HttpResponse('Студент не подавал заявки на этот проект или её состояние уже изменено')
    return redirect('project', project_id=project_id)


def decline_app(request, student_id, project_id):
    student = TeamMember.objects.get(pk=student_id)
    project = Project.objects.get(pk=project_id)
    if student.state == TeamMember.State.OBSERVED and student.current_project.pk == project_id:
        try:
            student.state = TeamMember.State.REJECTED
            student.save()
            send_mail(
                'Изменение статуса участника',
                f"Ваш статус в проекте {project.name_of_project} изменён: ваша заявка отклонена менеджером.",
                'nikitashlapak04@gmail.com',
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
            # try:
                data = form.cleaned_data
                data['current_project'] = project
                data['state'] = TeamMember.State.OBSERVED
                student = TeamMember.objects.create(**data)
                send_mail(
                    'Заявка на проект подана успешно',
                    f"Вы успешно подали заявку на проект {project.name_of_project}. Вы получите уведомление о её принятии или отклонении менеджером.",
                    'nikitashlapak04@gmail.com',
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
                    'nikitashlapak04@gmail.com',
                    [project.manager_email],
                    fail_silently=False,
                )
                return render(request, 'main/reg_success.html')
            # except:
            #     form.add_error(None, 'Ошибка регистрации пользователя')
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
                    'nikitashlapak04@gmail.com',
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


