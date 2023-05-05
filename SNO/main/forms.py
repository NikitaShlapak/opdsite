from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.forms import CheckboxSelectMultiple

from .models import *

class UserCheckboxSelectMultiple(CheckboxSelectMultiple):
    template_name = "widgets/multiple_input_modified.html"
    pass


class ProjectCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_type'].empty_label = 'Укажите тип проекта'
        self.fields['implementation_period'].empty_label = 'Укажите сроки реализации проекта'

    class Meta:
        model = Project
        fields = ['name_of_project', 'project_type',  'target_groups',
                  'implementation_period', 'short_project_description', 'long_project_description', 'poster']
        widgets = {
            'name_of_project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Проект проект"}),
            'target_groups': UserCheckboxSelectMultiple(),
            'short_project_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Краткое (до 150 символов) описание проекта"}),

            'long_project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                              'placeholder': "Полное описание проекта. \nНе сдерживайте себя!\nПрямо совсем не сдерживайте"}),

            'poster': forms.FileInput(attrs={'class': 'form-control h-100'}),

            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'implementation_period': forms.Select(attrs={'class': 'form-control'}),




        }

class ProjectEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_type'].empty_label = 'Укажите тип проекта'
        self.fields['implementation_period'].empty_label = 'Укажите сроки реализации проекта'

    class Meta:
        model = Project
        fields = ['name_of_project', 'project_type', 'target_groups',
                  'implementation_period', 'short_project_description', 'long_project_description', ]
        widgets = {
            'name_of_project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Проект проект"}),
            'target_groups': UserCheckboxSelectMultiple(),
            'short_project_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Краткое (до 150 символов) описание проекта"}),

            'long_project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                              'placeholder': "Полное описание проекта. \nНе сдерживайте себя!\nПрямо совсем не сдерживайте"}),

            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'implementation_period': forms.Select(attrs={'class': 'form-control'}),


        }

class ProjectRejectForm(forms.Form):
   reason = forms.CharField(label="Причина отклонения",max_length=125, widget=forms.TextInput(attrs={'class': 'form-control'}))
   comment = forms.CharField(label="Комментарий", widget=forms.Textarea(attrs={'rows': 3,'class': 'form-control'}))
   hide_name = forms.BooleanField(label='Скрыть моё имя в письме куратору',widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),required=False)



class ProjectReportForm(forms.ModelForm):

    class Meta:
        model = ProjectReport
        fields = ['heading', 'text', 'file']
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    group = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                          'placeholder': "Учебная группа",
                                                                          'aria-describedby': "button-addon"}))


class SearchNameForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                         'placeholder': "Введите часть названия или фамилии куратора",
                                                                         'aria-describedby': "button-addon2"}))


class ProjectReporkMarkingForm(forms.ModelForm):
    class Meta:
        model = ProjectReportMark
        fields = ['value', 'comment']

        widgets = {
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }