import logging
import sys

import requests
import vk_api
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.edit import FormView

from .models import VKTokenConnection

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
from SNO.vk_env import VK_SCOPES, VK_ID, VK_LOGIN_REDIRECT_URI, VK_SECRET

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

class LinkVkView(DataMixin, View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='register')
        return context | c_def
    def get(self, request, *args,**kwargs):
        print(request.GET, request.read(),sep='\n')
        if request.GET:
            print('Запрос токена...\n',request.GET)
            if request.GET['code']:
                data = {'code':request.GET['code'],
                        'client_id': VK_ID,
                        'client_secret':VK_SECRET,
                        'redirect_uri':VK_LOGIN_REDIRECT_URI}
                print(data)
                req = requests.get(url='https://oauth.vk.com/access_token', params=data)
                print('Ответ на запрос токена:',req.json())
                return self.post(request, **req.json())
            #vk_session = vk_api.VkApi('+71234567890', 'mypassword')
        else:
            print('Запрос кода...')
            data = {'client_id': VK_ID,
                    'redirect_uri': VK_LOGIN_REDIRECT_URI,
                    'response_type':'token',
                    'v':'5.131',
                    'scope':VK_SCOPES,
                    }
            req = requests.get(url='https://oauth.vk.com/authorize', params=data)
            print('Адрес запроса:\n', req.url)

            # print('Результат запроса:\n', req.text)
            return redirect(req.url)
        return HttpResponse('GET OK')

    def post(self, request, *args, **kwargs):
        print(kwargs)
        connection, created = VKTokenConnection.objects.get_or_create(
            user_id=kwargs.pop('user_id'),
            defaults=kwargs
        )
        connection.save()
        return redirect('user_accounts:signup_vk', vk_id=connection.user_id)
        # return HttpResponse("POST OK")

class SignupWithVKView(DataMixin, FormView):
    form_class = CustomUserCreationForm
    template_name = 'account/signup.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='register')
        return context | c_def
    
    def get(self, request, *args, **kwargs):
        # print(request, args , kwargs)
        vk_id = kwargs['vk_id']
        connection = VKTokenConnection.objects.get(user_id=vk_id)
        vk_session = vk_api.VkApi(token=connection.access_token)
        vk = vk_session.get_api()
        info = vk.account.getProfileInfo()
        print(info)
        return super().get(request, args, kwargs)




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

