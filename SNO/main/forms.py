from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import *

class ProjectConfirmationForm(forms.Form):
   edition_key = forms.IntegerField(label="Ключ безопасности",widget=forms.TextInput(attrs={'class': 'form-control'}))

class ProjectRejectForm(forms.Form):
   edition_key = forms.IntegerField(label="Ключ безопасности",widget=forms.TextInput(attrs={'class': 'form-control'}))
   reason = forms.CharField(label="Причина отклонения",max_length=125, widget=forms.TextInput(attrs={'class': 'form-control'}))
   comment = forms.CharField(label="Комментарий",widget=forms.Textarea(attrs={'rows':10,'class': 'form-control'}))


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ['username', 'password1', 'password2','last_name', 'first_name', 'email', 'study_group']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'study_group': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class TeamMemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'email', 'study_group']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'study_group': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }



class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_type'].empty_label = 'Укажите тип проекта'
        self.fields['implementation_period'].empty_label = 'Укажите сроки реализации проекта'

    class Meta:
        model = Project
        fields = ['name_of_project', 'project_type', 'manager', 'target_groups', 'manager_email',
                  'implementation_period', 'short_project_description', 'long_project_description', 'poster']
        widgets = {
            'name_of_project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Проект проект"}),
            'target_groups': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Учебные группы, для которых предназначен проект"}),
            'short_project_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Краткое (до 150 символов) описание проекта"}),

            'long_project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                              'placeholder': "Полное описание проекта. \nНе сдерживайте себя!\nПрямо совсем не сдерживайте"}),

            'poster': forms.FileInput(attrs={'class': 'form-control h-100'}),

            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'implementation_period': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'selectpicker js-states form-control', 'data-live-search': 'true'}),

            'manager_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "somemail@oiate.ru"}),

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
            'target_groups': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Учебные группы, для которых предназначен проект"}),
            'short_project_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Краткое (до 150 символов) описание проекта"}),

            'long_project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                              'placeholder': "Полное описание проекта. \nНе сдерживайте себя!\nПрямо совсем не сдерживайте"}),



            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'implementation_period': forms.Select(attrs={'class': 'form-control'}),


        }


class ProjectReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].empty_label = 'Автор не указан'

    class Meta:
        model = ProjectReport
        fields = ['heading', 'text', 'file', 'author']
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'selectpicker js-states form-control', 'data-live-search': 'true'}),
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
