from .models import *

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
    return title

def find_by_group(all_projects=Project.objects.exclude(project_status=Project.ProjectStatus.REJECTED), group='group'):
    projects = []
    for p in all_projects:
        print(p.target_groups, group, group.upper() == p.target_groups.upper())
        if group.upper() in p.target_groups.upper():
            projects.append(p)
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