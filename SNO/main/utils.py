import random

from django.forms import CheckboxSelectMultiple

from SNO.settings import SNO_EVENTS_ACTIVE
from SNO.vk_env import VK_SCOPES, VK_ID, VK_LOGIN_REDIRECT_URI
from user_accounts.models import CustomUser, StudyGroup

from .forms import SearchForm, SearchNameForm
from .models import Project
from .standalone_utils import form_title


class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        context['group_form'] = SearchForm()
        context['name_form'] = SearchNameForm()
        context['events_active'] = SNO_EVENTS_ACTIVE
        if 'selected' not in context:
            context['selected'] = 'all'
        context['title'] = form_title(context['selected'])
        context['login_with_vk_link'] = f'https://oauth.vk.com/authorize?client_id={VK_ID}&redirect_uri={VK_LOGIN_REDIRECT_URI}&response_type=code&v=5.131'
        for scope in VK_SCOPES:
            context['login_with_vk_link'] = context['login_with_vk_link'] + f'&scope={scope}'
        return context


def find_by_group(all_projects=Project.objects.all(), search='group'):
    # print(search)

    projects = []
    for project in all_projects:
        # print(project.get_all_target_group_types(), search.upper())
        if search.upper() in project.get_all_target_group_types().upper():
            if not project in projects:
                projects.append(project)
    return projects

def find_by_name(all_projects=Project.objects.all(), data='null'):
    projects = []
    for p in all_projects:
        # print(p.name_of_project, p.manager.get_full_name, data)
        if data.upper() in p.name_of_project.upper() or data.upper() in p.manager.get_full_name().upper():
            projects.append(p)
    return projects

def generate_edition_key():
    key = random.randint(1000,32767)
    if Project.objects.filter(edition_key=key).exists():
        generate_edition_key()
    else:
        return key

def user_can_mark_reports(user:CustomUser, project:Project):
    if not user.is_authenticated:
        return False
    if not user.is_superuser:
        print(user.study_group.type)
        if not user.study_group.type == StudyGroup.StudyGroupType.TEACHER:
            return False
        else:
            group_match = False
            for user_group in user.studygrop_set.all():
                if user_group.type in project.get_all_target_group_types_list():
                    group_match = True
            if not group_match:
                return False
    return True

def get_all_unmarked_reports(user:CustomUser, project:Project):
    if user.study_group.type != StudyGroup.StudyGroupType.TEACHER:
        return None
    else:
        reports = []
        for report in project.projectreport_set.all():
            try:
                mark = report.projectreportmark_set.get(author=user)
            except:
                if report.author != user:
                    reports.append(report)
            else:
                pass
                # print(mark)
        return reports

def get_all_report_marks(user:CustomUser, project:Project):
    if user.study_group.type != StudyGroup.StudyGroupType.TEACHER:
        return None
    else:
        marks = []
        for report in project.projectreport_set.all():
            try:
                mark = report.projectreportmark_set.get(author=user)
            except:
                # print(report)
                pass
            else:
                if report.author != user:
                    marks.append(mark)
        return marks


