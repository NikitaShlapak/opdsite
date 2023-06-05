import logging
import sys

import requests
import vk_api
from django.http import HttpResponse
from django.views.generic.base import View

sys.path.append("..")
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth import logout as django_logout


from .forms import CustomUserCreationForm, CustomUserAuthenticationForm
from main.utils import DataMixin, get_all_unmarked_reports, get_all_report_marks
from main.models import Project, Applications
from main.forms import SearchForm

logging.basicConfig(level=logging.INFO, filename="main_views.log",filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


def page_not_found_view(request, exception):
    data = {
        'group_form': SearchForm(),
        'exeption': exception
    }
    return render(request,'404.html', context=data)


class RegisterUser(DataMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = "main/register+login.html"
    success_url = reverse_lazy('user_accounts:login')

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

class LoginWithVkView(View):

    def get(self, request, *args,**kwargs):
        print(request.GET, args, kwargs, request.method, request,sep='\n')
        if request.GET['code']:
            data = {'code':request.GET['code'],
                    'client_id':'51666712',
                    'client_secret':'vl71x7P1SfdJ6pEwgQMM',
                    'redirect_uri':'http://127.0.0.1:8000/accounts/login/vk/'}
            print(data)
            req = requests.get(url=f'https://oauth.vk.com/access_token', params=data)
            print(req.json())
        #vk_session = vk_api.VkApi('+71234567890', 'mypassword')
        return HttpResponse('OK')
    pass

def logout(request):
    django_logout(request)
    return redirect('user_accounts:login')

class ProfilePage(DataMixin, LoginRequiredMixin, ListView):
    template_name = 'user_accounts/profile_page.html'
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
        unmarked_reports = []
        for project in Project.objects.all():
            if get_all_unmarked_reports(self.request.user,project):
                unmarked_reports.append({'project':project,
                                         'reports':get_all_unmarked_reports(self.request.user,project)})
        report_marks = []
        for project in Project.objects.all():
            if get_all_report_marks(self.request.user, project):
                report_marks.append({'project': project,
                                      'marks': get_all_report_marks(self.request.user, project)})
        if unmarked_reports:
            context['unmarked_reports']=unmarked_reports
        if report_marks:
            context['marked_reports']=report_marks
        c_def = self.get_user_context(selected='profile')
        return context|c_def

    def handle_no_permission(self):
        return redirect('user_accounts:login')

