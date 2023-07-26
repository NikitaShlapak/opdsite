from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.forms import CheckboxSelectMultiple

from .models import *

class UserCheckboxSelectMultiple(CheckboxSelectMultiple):
    template_name = "widgets/multiple_input_modified.html"
    pass

class CustomUserCreationForm(SignupForm):

    study_group = forms.ModelChoiceField(queryset=StudyGroup.objects.all(), label='Учебная группа')
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')
    email = forms.EmailField(label='Почта')

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super().save(request)
        print(user.__dict__, self.cleaned_data)
        # Add your own processing here.
        user.study_group = self.cleaned_data['study_group']
        user.save()
        # You must return the original result.
        return user

    class Meta(SignupForm):
        model = CustomUser
        fields = ['username', 'password1', 'password2','last_name', 'first_name', 'email', 'study_group']
        widgets = {
            'login': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'},),
            'study_group': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class CustomUserAuthenticationForm(LoginForm):
    login = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def login(self, *args, **kwargs):

        # Add your own processing here.
        print(args[0].POST, kwargs)
        # You must return the original result.
        return super().login(*args, **kwargs)

    class Meta(LoginForm):
        model = CustomUser


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'study_group')




