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
from django.views.generic import UpdateView, CreateView, DetailView, TemplateView, ListView, FormView
from django.contrib.auth import logout as django_logout

from .models import *
from .forms import *
from .utils import *


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


def Info(request):
    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'selected': 'info'
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/info.html', context=data)


class ProjectCreationView(DataMixin, LoginRequiredMixin, CreateView):
    form_class = ProjectCreationForm
    template_name = "main/add_project.html"

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='add')
        return context|c_def

    def post(self,request, **kwargs):
        form = ProjectCreationForm(request.POST, request.FILES)
        if form.is_valid():
            if len(form.cleaned_data['long_project_description']) > len(form.cleaned_data['short_project_description']):
                groups = form.cleaned_data.pop('target_groups')
                try:
                    pr = Project.objects.create(edition_key=generate_edition_key(),
                                                manager=request.user,
                                                **form.cleaned_data)
                    for group in groups:
                        pr.target_groups.add(group)
                    pr.save()
                    logging.info(f"Successfully created project {pr}. Manager - {request.user}")
                    return redirect('project', pr.pk)
                except:
                    form.add_error(None, 'Ошибка регистрации проекта')
            else:
                form.add_error(None, 'Длинное описание проекта не может быть короче краткого!')
        return render(request, self.template_name, context={'form':form})


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






class ProjectUpdateView(DataMixin, LoginRequiredMixin, UpdateView):
    model = Project
    template_name = "main/edit_project.html"
    pk_url_kwarg = 'project_id'
    context_object_name = 'p'
    form_class = ProjectEditForm

    def get(self, request, **kwargs):
        self.extra_context={'project':get_object_or_404(Project, pk=kwargs['project_id'])}
        print(kwargs)
        return super().get(request, **kwargs)

    def post(self, request, *args, **kwargs):
        self.extra_context = {'project': get_object_or_404(Project, pk=kwargs['project_id'])}
        return super().post(request,*args, **kwargs)

    def form_valid(self, form):
        project = self.extra_context['project']
        old_groups = project.target_groups.all()
        new_groups = form.cleaned_data.pop('target_groups')

        updated_fields = []
        for field in form.cleaned_data:
            if not form.cleaned_data[field]==project.__dict__[field]:
                updated_fields.append(field)
        if list(old_groups) != list(new_groups):
            updated_fields.append('target_groups')
        if not updated_fields:
            form.add_error(None, 'Вы ничего не изменили')
            return self.form_invalid(form)

        if len(form.cleaned_data['long_project_description']) > len(form.cleaned_data['short_project_description']):
            try:
                Project.objects.filter(pk=project.pk).update(**form.cleaned_data)
                if project.project_status == Project.ProjectStatus.REJECTED:
                    project.project_status = Project.ProjectStatus.UNDERREVIEW
                    project.save()
                if list(old_groups) != list(new_groups):
                    project.target_groups.clear()
                    project.target_groups.add(*new_groups)
                    project.save()
            except:
                logging.error(f"Can not update project {project}. User: {self.request.user.username}")
                return redirect('project', project.pk)
            else:
                logging.info(f"Successfully updated project {project}. User: {self.request.user.username}.\n{updated_fields=}")
                return redirect('project', project.pk)
        else:
            form.add_error(None, 'Длинное описание проекта не может быть короче краткого!')
            return self.form_invalid(form)
        return HttpResponse(', '.join(updated_fields))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='register')
        return context | c_def

    def handle_no_permission(self):
        return redirect('login')

class SetProjectStatusView(DataMixin, LoginRequiredMixin, View):
    def handle_no_permission(self):
        return redirect('login')
    def get(self, request, **kwargs):
        project = get_object_or_404(Project,pk=kwargs['project_id'])
        if not (request.user.is_staff or request.user.is_superuser):
            self.handle_no_permission()
        else:
            if kwargs['action'] == 'confirm':
                status = project.ProjectStatus.ENROLLMENTOPENED
            elif kwargs['action'] == 'close':
                status = project.ProjectStatus.ENROLLMENTCLOSED
            elif kwargs['action'] == 'delete':
                try:
                    project.delete()
                except:
                    logging.error(f"Can not delete project {project}. User: {request.user.username}")
                    return redirect('MAIN')
                else:
                    logging.info(f"Successfully deleted project {project} by {request.user.username}")
                    return redirect('profile')
            try:
                project.project_status = status
                project.save()
            except:
                logging.error(f'Can not set status to "{status}". Project: {project}. User: {request.user}')
            else:
                logging.info(f"Project status set to '{status}'. Project: {project}. User: {request.user}")
            return redirect('project', project.pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = context | c_def
        return context


class RejectProjectView(DataMixin, LoginRequiredMixin, DetailView, FormView):
    template_name = 'main/project_page.html'
    model = Project
    pk_url_kwarg = 'project_id'
    context_object_name = 'p'

    form_class = ProjectRejectForm
    success_url = '/accounts/profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='register')
        context = context | c_def
        self.extra_context['project'] = context['p']
        return context

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        data = form.cleaned_data
        project = self.extra_context['project']
        user = self.extra_context['user']

        letter_context = {
            'title': f"Изменение статуса проекта {project.name_of_project}",
            'text': [f'Ваш проект {project.name_of_project} был отклонён']
        }
        if not data['hide_name']:
            letter_context['text'][0] = letter_context['text'][0] + f" пользователем {user.get_full_name()}"
        letter_context['text'][0] = letter_context['text'][0] + '.'
        letter_context['text'].append(f"Причина:\n{data['reason']}.")
        letter_context['text'].append(f"Комментарий:\n{data['comment']}.")
        letter_context['text'].append(f"Личный кабинет: ")  # TODO insert profile link

        project.manager.email_user(subject=f"Изменение статуса проекта {project.name_of_project}", message=f'test',
                                   html_message=render_to_string(request=self.extra_context['request'],
                                                                 template_name='letter_base.html',
                                                                 context=letter_context))
        logging.info(
            f"Project declined. User: {user}, Project: {project.name_of_project}, message:{letter_context['text']}")
        project.project_status = project.ProjectStatus.REJECTED
        project.save()
        return super().form_valid(form)

    def post(self, request, **kwargs):
        self.extra_context = {'project': get_object_or_404(Project, pk=kwargs['project_id']),
                              'user': request.user,
                              'request': request}
        return super().post(request, **kwargs)





def AddReport(request, project_id): # TODO: refactor to class
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

