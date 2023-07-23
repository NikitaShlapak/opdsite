import logging
import sys

import requests
import vk_api
from allauth.socialaccount.models import SocialAccount
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.edit import FormView
from transliterate import translit

from .models import VKTokenConnection, CustomUser

sys.path.append("..")
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth import logout as django_logout, login

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





class LinkVkView(DataMixin, View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='register')
        return context | c_def
    def get(self, request, *args,**kwargs):
        if request.GET:
            if request.GET['code']:
                data = {'code':request.GET['code'],
                        'client_id': VK_ID,
                        'client_secret':VK_SECRET,
                        'redirect_uri':VK_LOGIN_REDIRECT_URI}
                req = requests.get(url='https://oauth.vk.com/access_token', params=data)
                return self.post(request, **req.json())
        else:
            data = {'client_id': VK_ID,
                    'redirect_uri': VK_LOGIN_REDIRECT_URI,
                    'response_type':'code',
                    'v':'5.131',
                    'scope':VK_SCOPES,
                    }
            req = requests.get(url='https://oauth.vk.com/authorize', params=data)
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

class SignupWithVKView(DataMixin, FormView):
    form_class = CustomUserCreationForm
    template_name = 'socialaccount/signup.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(selected='register')
        return context | c_def
    
    def get(self, request, *args, **kwargs):
        vk_id = kwargs['vk_id']
        connection = VKTokenConnection.objects.get(user_id=vk_id)
        vk_session = vk_api.VkApi(token=connection.access_token)
        vk = vk_session.get_api()
        info = vk.users.get(user_ids=connection.user_id)[0]
        self.initial = {"first_name":info['first_name'],
                        'last_name':info['last_name'],
                        'email':connection.email,
                        'username':translit(f"{info['first_name'].capitalize()}{info['last_name'].capitalize()}@{vk_id}", language_code='ru', reversed=True),
                        }
        return super().get(request, args, kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        study_group = data.pop('study_group')
        password = data.pop('password1')
        data.pop('password2')
        try:
            user = CustomUser.objects.create(**data, password=password, study_group=study_group)
        except:
            logging.error('Can not create user')
        else:
            login(self.request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            logging.info(f'User {user} logged in. Trying to link VK profile...')
            try:
                connection = VKTokenConnection.objects.get(email=user.email)
            except:
                logging.error('VK connection does not exist!')
            else:
                logging.info(f'Connection found: {connection.email=}, {connection.user_id=}')
                vk_session = vk_api.VkApi(token=connection.access_token)
                vk = vk_session.get_api()
                info = vk.users.get(user_ids=connection.user_id)[0]
                acc, created = SocialAccount.objects.get_or_create(uid=connection.user_id, defaults={
                    'user':user,
                    'provider':'vk',
                    'extra_data':info
                })
                logging.info(f'User {user} succesfully signed up, logged in and connection to vk_id @{connection.user_id} created')
        return redirect('profile')




def logout(request):
    django_logout(request)
    return redirect('login')

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
        context['managed_applies'] = Applications.objects.filter(project__pk__in=my_project_ids).order_by('-pk')
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


