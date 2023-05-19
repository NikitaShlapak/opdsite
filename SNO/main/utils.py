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
    if page == 'marking':
        title = 'Оценка отчёта | Report marking'
    return title

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


class WikiPlainHTMLTextTransformer:
    def fit(self, text:str):
        return self.fit_plain(text)
    def fit_plain(self, text:str):
        text = text.replace(self.u[0], '<u>').replace(self.u[1], '</u>').replace(self.i[0], '<i>').replace(self.i[1], '</i>').replace(self.b[0], '<b>').replace(self.b[1], '</b>').replace(self.hr, '<hr>')
        text = text.replace(self.olist[0], '<ol>').replace(self.olist[-1], '</ol>').replace(self.ulist[0], '<ul>').replace(self.ulist[-1], '</ul>')
        text = text.replace(self.olist[1], '<li>').replace(self.olist[2], '</li>').replace(self.ulist[1], '<li>').replace(self.ulist[2], '</li>')
        text = text.replace(self.table[0], '<table class="table table-primary table-bordered text-center align-middle">').replace(self.table[-1], '</table>')
        text = text.replace(self.table[1], '<tr>').replace(self.table[2], '<td>').replace(self.table[3], '</tr>').replace(self.table[4], '</td>')
        text_split = text.split('\r\n')
        new_text = ''
        for i in range(len(text_split)):
            line = text_split[i]
            print(f"1|{line}|")
            if not len(line):
                line = '<br>'
            if line.startswith(self.h):
                if line.startswith(self.h * 2):
                    if line.startswith(self.h * 3):
                        line = f'<h6>{line[3:]}</h6>'
                    else:
                        line = f'<h5>{line[2:]}</h5>'
                else:
                    line = f'<h4>{line[1:]}</h4>'

            if         line.startswith('<br>') \
                    or line.startswith('<h') \
                    or line.startswith('<ol>') or line.startswith('</ol>') \
                    or line.startswith('<ul>') or line.startswith('</ul>') \
                    or line.startswith('<li>') or line.startswith('</li>')  \
                    or line.startswith('<table') or line.startswith('</table>') \
                    or line.startswith('<tr>') or line.startswith('</tr>') \
                    or line.startswith('<td>') or line.startswith('</td>'):
                pass
            else:
                if new_text:
                    new_text = new_text+'<br>'
            new_text = new_text + line
        return new_text


    def __init__(self,
                     h = '#',
                     u = '{{ }}'.split(' '),
                     i = '(( ))'.split(' '),
                     b = '[[ ]]'.split(' '),
                     hr = '---',
                     olist = '<<olist>> <<newline>> <<endline>> <<endolist>>'.split(' '),
                     ulist = '<<ulist>> <<newline>> <<endline>> <<endulist>>'.split(' '),
                     table = '<<table>> <<newrow>> <<newcol>> <<endrow>> <<endcol>> <<endtable>>'.split(' ')
                 ):
        self.h = h
        self.u = u
        self.i = i
        self.b = b
        self.hr = hr
        self.olist = olist
        self.ulist = ulist
        self.table = table