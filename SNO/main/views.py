import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, CreateView, DetailView, TemplateView, ListView
from django.contrib.auth import logout as django_logout

from .models import *
from .forms import *
from .utils import *
from SNO.env import EMAIL_HOST_USER

logging.basicConfig(level=logging.INFO, filename="main_views.log",filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


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



class ProjectView(DataMixin, DetailView):
    template_name = 'main/project_page.html'
    model = Project
    pk_url_kwarg = 'project_id'
    context_object_name = 'p'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected=context['p'].project_type,
                                      desc=context['p'].long_project_description.split('\n'),
                                      reject_form=ProjectRejectForm(),
                                      applyies=Applications.objects.filter(project__pk=context['p'].pk).order_by('-pk'))
        context['user'] = self.request.user
        return context | c_def



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
    # print(request.method)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        # print(form.is_valid())
        # print(form.errors)
        # print(form.cleaned_data)
        if form.is_valid():
            # print(form.cleaned_data)
            if len(form.cleaned_data['long_project_description']) > len(form.cleaned_data['short_project_description']):
                # if (form.cleaned_data['manager'].current_project):
                #     form.add_error(None,
                #                    'Этот студент не может быть менеджером проекта, так как уже подал заявку в другой '
                #                    'или является менеджером')
                # else:
                    try:
                        groups = form.cleaned_data.pop('target_groups')
                        pr = Project.objects.create(edition_key=generate_edition_key(),**form.cleaned_data)
                        print(groups)
                        # for group in groups:
                        #     pr.target_groups.add(group)
                        pr.target_groups.add(groups)
                        pr.save()

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


class ConfirmOrDeclineApplication(DataMixin,LoginRequiredMixin,TemplateView):
    def handle_no_permission(self):
        return redirect('login')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user']=self.request.user

        c_def = self.get_user_context()
        return context|c_def
    def get(self, request, **kwargs):
        app = get_object_or_404(Applications, pk=kwargs['app_id'])
        manager = request.user
        if app.project.manager == manager or (kwargs['action'] == 'delete' and app.user==manager) or manager.is_superuser:
            letter_context = {
                'title': f"Изменение статуса заявки на проект {app.project.name_of_project}",
            }
            if kwargs['action'] == 'confirm':
                try:
                    app.project.team.add(app.user)
                    app.project.save()
                    logging.info(f"Succefully added {app.user} to {app.project} team")
                except:
                    logging.error(f"Can not add {app.user} to {app.project} team")
                else:
                    letter_context['text']=f"Ваша заявка принята!\nПоздравляем, теперь вы в команде проекта {app.project}!\nСтраница проекта:".split('\n') #TODO: add link to project
                    app.user.email_user(subject=f"Изменение статуса заявки ", message=f'test',
                               html_message=render_to_string(request=request, template_name='letter_base.html', context=letter_context))
                    app.delete()

            elif kwargs['action'] == 'delete':
                reclaim = (app.user == request.user)
                try:
                    app.delete()
                    logging.info(f"Succefully deleted application: {app}")
                except:
                    logging.error(f"Can not deleted application: {app}")
                else:
                    if not reclaim:
                        letter_context[
                            'text'] = f"Ваша заявка отклонена менеджером!\nК сожалению, ваша заявка на проект {app.project} была отклонена пользователем {manager.username}".split(
                            '\n')
                        app.user.email_user(subject=f"Изменение статуса заявки ", message=f'test',
                                            html_message=render_to_string(request=request, template_name='letter_base.html',
                                                                          context=letter_context))
        else:
            logging.info(f"{manager} tried to fuck YOU! (attempt to {kwargs['action']} an application {app=}")
            self.handle_no_permission()
        return redirect('profile')





class CreateApplication(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'main/add_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user']=self.request.user

        c_def = self.get_user_context()
        return context|c_def
    def handle_no_permission(self):
        return redirect('login')
    def get(self, request, **kwargs):
        project = Project.objects.get(pk=kwargs['project_id'])
        context = self.get_context_data(selected=project.project_type,project=project)

        # if request.user in project.team.all():
        #     return

        app, context['created'] = Applications.objects.get_or_create(project=context['project'],user=request.user)

        app.save()

        if context['created']:
            letter_context ={
                'title':f"Заявка на проект {project.name_of_project}",
                'text':[f'На ваш проект {project.name_of_project} подали заявку.',
                        'Информация о студенте:',
                        f"{request.user.get_full_name()}, группа {request.user.study_group}.",
                        f"Управление заявками: " #TODO: insert link to profile page
                        ]
            }
            project.manager.email_user(subject=f"Заявки на проект {project.name_of_project}", message=f'test',
                                   html_message=render_to_string(request=request, template_name='letter_base.html', context=letter_context))
            logging.info(f'Application created. User: {request.user}, Project: {project.name_of_project}')

        return render(request, self.template_name, context=context)




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


def reject_project(request, project_id): #TODO refactor to class
    project = Project.objects.get(pk=project_id)
    if request.method == 'POST':
        form = ProjectRejectForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['edition_key']
            # print(form.cleaned_data)
            if key == project.edition_key:

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



class ProjectUpdateView(UpdateView): #TODO: hard refactor
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

class ProfilePage(DataMixin, LoginRequiredMixin, ListView):
    template_name = 'main/profile_page.html'
    model = Project
    context_object_name = 'managed_projects'

    def get_queryset(self):
        return Project.objects.filter(manager=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user']=self.request.user
        context['projects']=self.request.user.project_set.all()
        context['my_applies'] = Applications.objects.filter(user=self.request.user)
        my_projects = Project.objects.filter(manager=self.request.user)
        my_project_ids=[]
        for project in my_projects:
            my_project_ids.append(project.pk)
        # print(my_project_ids)
        context['managed_applies'] = Applications.objects.filter(project__pk__in=my_project_ids).order_by('-pk')
        # print(len(context['managed_applies']))

        c_def = self.get_user_context(selected='profile')
        return context|c_def

    def handle_no_permission(self):
        return redirect('login')

