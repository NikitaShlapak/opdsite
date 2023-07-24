import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup as bs

from django.core.management.base import BaseCommand
from django.utils import timezone

from user_accounts.models import StudyGroup


class Command(BaseCommand):
    help = 'Parsing all groups from http://timetable.iate.obninsk.ru/ and creating/updating groups of previous and current year'

    def handle(self, *args, **kwargs):
        logging.info('Groups parsing initiated...')
        print('Groups parsing initiated...')
        created = 0
        groups = get_all_groups()
        groups_dict = []
        types = []
        for id, group_name in groups:
            type = re.match(r'[а-яА-Я]*', group_name).group(0)
            types.append(type)
            course = re.search(r'-[А-Я]\d', group_name).group(0)[1]
            year = '20'+re.search(r'-[А-Я]\d\d', group_name).group(0)[-2:]

            numgroup_re = re.match(r'[а-яА-Я]*\d', group_name)
            if numgroup_re:
                numgroup = numgroup_re.group(0)[-1]
            else:
                numgroup=0

            is_foreigns = group_name[-1]=='и'

            groups_dict.append({
                'group_name': group_name,
                'type':  type,
                'course': course,
                'year':year,
                'numgroup': numgroup,
                'is_foreigns':is_foreigns,
                'timetable_id':id
            })
            if int(year) >= datetime.today().year-1:
                if not course in (StudyGroup.StudyGroupCourseType.ASP, StudyGroup.StudyGroupCourseType.MAG):
                    created = created + create_group(**groups_dict[-1], subgroup=1)
                    created = created + create_group(**groups_dict[-1], subgroup=2)
        print(f'total groups processed: {len(groups_dict)}\n{created} groups created')


def get_all_groups():
    data = requests.get('http://timetable.iate.obninsk.ru/')
    soup = bs(data.text, 'html.parser')
    links = soup.findAll(href=re.compile("group"))
    resp = []
    for link in links:
        resp.append((link['href'].split('/')[-1],link.text))
    return resp

def create_group(group_name:str,**kwargs):
    gr, created = StudyGroup.objects.get_or_create(**kwargs)
    gr.set_institute()
    gr.save()
    logging.info(f'Group {gr} created/updated')
    return int(created)
