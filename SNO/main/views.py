import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from django.views import View
from django.views.generic import UpdateView, CreateView, DetailView, TemplateView, FormView

from SNO.settings import SNO_EVENTS_ACTIVE
from .env import MAX_UPLOAD_FILE_SIZE, ALLOWED_CONTENT_TYPES
from .forms import *


from .standalone_utils import form_title, WikiPlainHTMLTextTransformer
from .utils import find_by_group, find_by_name, DataMixin, user_can_mark_reports, generate_edition_key

logging.basicConfig(level=logging.INFO, filename="main_views.log",filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


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
            projects = find_by_group(all_projects=projects, search=request.GET['group'])
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
        'events_active': SNO_EVENTS_ACTIVE
    }
    data['title']= form_title(data['selected'])

    return render(request, 'main/index.html', context=data)




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
        'events_active': SNO_EVENTS_ACTIVE
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/index.html', context=data)


def Info(request):

    group_form = SearchForm()
    data = {
        'group_form': group_form,
        'selected': 'info',
        'events_active': SNO_EVENTS_ACTIVE
    }
    data['title'] = form_title(data['selected'])
    return render(request, 'main/info.html', context=data)


class ProjectView(DataMixin, DetailView):
    template_name = 'main/project_page.html'
    model = Project
    pk_url_kwarg = 'project_id'
    context_object_name = 'p'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = context['p']
        user = self.request.user
        reports_marked=[]
        for report in project.projectreport_set.all():
            mark = []
            try:
                marks = report.projectreportmark_set.filter(author=user)
                mark = marks[0]
            except:
                pass
            reports_marked.append({'report':report, 'mark':mark})

        conv = WikiPlainHTMLTextTransformer()
        c_def = self.get_user_context(selected=project.project_type,

                                      reject_form=ProjectRejectForm(),
                                      applyies=Applications.objects.filter(project__pk=project.pk).order_by('pk'),
                                      reports=reports_marked,
                                      reports_markable=user_can_mark_reports(user,project))
        context['user'] = user
        return context | c_def

    def get(self, request, *args,**kwargs):
        text = Project.objects.get(pk=kwargs[self.pk_url_kwarg]).long_project_description
        conv = WikiPlainHTMLTextTransformer()
        # print(conv)
        conv.fit(text)
        return super().get(request, *args, **kwargs)



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
                    if request.user.is_approved:
                        pr.project_status = Project.ProjectStatus.ENROLLMENTOPENED
                    pr.save()
                except:
                    form.add_error(None, 'Ошибка регистрации проекта')
                else:
                    logging.info(f"Successfully created project {pr}. Manager - {request.user}")
                    return redirect('project', pr.pk)

            else:
                form.add_error(None, 'Длинное описание проекта не может быть короче краткого!')
        return render(request, self.template_name, context={'form':form})


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
                project.project_status = Project.ProjectStatus.UNDERREVIEW
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

class SetProjectStatusView(DataMixin, LoginRequiredMixin, View):

    def get(self, request, **kwargs):
        project = get_object_or_404(Project,pk=kwargs['project_id'])
        if not (request.user.is_staff or request.user.is_superuser or request.user == project.manager):
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

    # def handle_no_permission(self):
    #     return redirect('user_accounts:login')

    def form_valid(self, form):
        data = form.cleaned_data
        project = self.extra_context['project']
        user = self.extra_context['user']

        letter_context = {
            'title': f"Изменение статуса проекта {project.name_of_project}",
            'text': [f'Ваш проект {project.name_of_project} был отклонён']
        }

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




class CreateApplication(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'main/add_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user']=self.request.user

        c_def = self.get_user_context()
        return context|c_def
    # def handle_no_permission(self):
    #     return redirect('user_accounts:login')
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
    # def handle_no_permission(self):
    #     return redirect('user_accounts:login')
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



class ReportCreateView(DataMixin, LoginRequiredMixin,DetailView, FormView):
    model = Project
    pk_url_kwarg = 'project_id'
    context_object_name = 'p'

    form_class = ProjectReportForm
    success_url = '/accounts/profile'

    template_name = 'main/add_coment.html'
    project=None

    def post(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        self.object = get_object_or_404(Project, pk=kwargs['project_id'])
        return super().post(request,*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = context['p']
        reports_marked = []
        for report in project.projectreport_set.all():
            mark = []
            try:
                marks = report.projectreportmark_set.filter(author=self.request.user)
                mark = marks[0]
            except:
                pass
            reports_marked.append({'report': report, 'mark': mark})
        c_def = self.get_user_context(selected=project.project_type,
                                      reports = reports_marked,
                                      reports_markable=user_can_mark_reports(self.request.user, project),
                                      reject_form=ProjectRejectForm(),
                                      applyies=Applications.objects.filter(project__pk=context['p'].pk).order_by('pk'))
        context['user'] = self.request.user
        context = context | c_def
        return context

    # def handle_no_permission(self):
    #     return redirect('user_accounts:login')

    def form_valid(self, form):
        if not (self.request.user in self.project.team.all() or self.project.manager == self.request.user):
            form.add_error(None, "Вы не можете добавлять отчёты к этому проекту!")
            self.form_invalid(form)
        file = form.cleaned_data['file']
        if file:
            # print(f"{file.name=}, {file.size=}, {file.content_type=}")
            logging.info(f"{file.name=}, {file.size=}, {file.content_type=}")
            if not file.content_type in ALLOWED_CONTENT_TYPES:
                form.add_error('file', 'Недопустимый тип файла. Загружать можно только отчёты и презентации в форматах .pdf, .doc(x), .ppt(x).')
                return self.form_invalid(form)
            if file.size > MAX_UPLOAD_FILE_SIZE:
                form.add_error('file', 'Вы пытаетесь загрузить слишком большой файл! Максимальный размер - 25 Мб.')
                return self.form_invalid(form)
        try:
            report = ProjectReport.objects.create(**form.cleaned_data, author=self.request.user, parent_project=self.project)
        except:
            logging.error(f"Can not create report for project {self.project}. User: {self.request.user.username}")
            return redirect('accounts:profile')
        else:
            logging.info(f"Successfully created report {report} by {self.request.user.username}")
            return redirect('project', self.project.pk)



class ProjectReportMarkUpdateView(DataMixin, LoginRequiredMixin, FormView):
    model = ProjectReportMark
    template_name = 'main/marking.html'
    context_object_name = 'r'
    form_class = ProjectReporkMarkingForm
    success_url = '/accounts/profile'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='marking', **{self.context_object_name:self.object.related_report,
                                                           'form':self.form_class(),
                                                           'p':self.object.related_report.parent_project,
                                                           'mark':self.object})
        context[self.context_object_name]=self.object.related_report
        context = context | c_def
        return context

    # def handle_no_permission(self):
    #     return redirect('user_accounts:login')


    def post(self, request, *args, **kwargs):
        report = get_object_or_404(ProjectReport, pk=kwargs['project_report_id'])
        self.object,created= ProjectReportMark.objects.get_or_create(author=request.user, related_report=report, defaults={'value':0})
        return super().post(request,*args, **kwargs)

    def get(self, request, *args, **kwargs):
        report = get_object_or_404(ProjectReport, pk=kwargs['project_report_id'])
        self.object, created = ProjectReportMark.objects.get_or_create(author=request.user, related_report=report, defaults={'value':0})
        return render(request,self.template_name, context={self.context_object_name:self.object.related_report,
                                                           'form':self.form_class(),
                                                           'p':self.object.related_report.parent_project,
                                                           'mark':self.object})
        
    def form_valid(self, form):
        data = form.cleaned_data
        if data['value']>100 or data['value']<1:
            form.add_error('value', 'Оценка не может быть ниже 1 или выше 100 баллов!')
            print('value error', form.errors)
            return self.form_invalid(form)
        else:
            self.object.value = data['value']
            try:
                self.object.save()
            except:
                logging.error(f"Can not save report mark for report {self.object}. User: {self.request.user.username}")
            else:
                logging.info(f"Succesfully saved report mark {self.object}. User: {self.request.user.username}. Value - {self.object.value} ")
            return redirect(self.object.get_absolute_url())

