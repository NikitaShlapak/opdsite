from django.forms import CheckboxSelectMultiple

from .forms import SearchForm, SearchNameForm
from .models import *



class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        context['group_form'] = SearchForm()
        context['name_form'] = SearchNameForm()
        if 'selected' not in context:
            context['selected'] = 'all'
        context['title'] = form_title(context['selected'])
        return context

def form_title(page='main'):
    title = 'Главная | Main'
    if page == 'opened':
        title = 'Открытые | Opened'
    if page =='closed':
        title = 'Закрытые | Closed'
    if page =='under_review' :
        title = 'На проверке | Under review'
    if page =='rejected':
        title = 'Отклонённые | Rejected'
    if page =='external':
        title = 'Внешние | External'
    if page =='service':
        title = 'Сервисные | Service'
    if page =='research':
        title = 'Исследовательские | Research'
    if page == 'register':
        title = 'Регистрация | Register'
    if page == 'login':
        title = 'Вход | Login'
    if page == 'profile':
        title = 'Личный кабинет | Profile'
    return title

def find_by_group(all_projects=Project.objects.all(), search='group'):
    print(search)
    projects = []
    for project in all_projects:
        print(project.get_all_target_group_types(), search.upper())
        if search.upper() in project.get_all_target_group_types().upper():
            if not project in projects:
                projects.append(project)
    return projects

def find_by_name(all_projects=Project.objects.all(), data='null'):
    projects = []
    for p in all_projects:
        print(p.name_of_project, p.manager.get_full_name, data)
        if data.upper() in p.name_of_project.upper() or data.upper() in p.manager.get_full_name().upper():
            projects.append(p)
    return projects

def generate_edition_key():
    key = random.randint(1000,32767)
    if Project.objects.filter(edition_key=key).exists():
        generate_edition_key()
    else:
        return key