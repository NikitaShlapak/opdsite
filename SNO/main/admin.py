from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name_of_project', 'manager', 'project_type', 'project_status', 'edition_key')
    list_display_links = ('name_of_project',)
    list_editable = ('project_status', )
    search_fields = ('name_of_project', 'manager__firstname', 'manager__secondname')
    sortable_by = ('name_of_project', 'project_type', 'project_status')

class ProjectReportAdmin(admin.ModelAdmin):
    list_display = ('parent_project', 'heading', 'author', 'text')
    list_display_links = ('heading',)
    search_fields = ('parent_project', 'author', 'text')
    sortable_by = ('parent_project','author')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username','first_name', 'last_name', 'study_group')
    list_display_links = ('first_name', 'last_name', 'study_group')
    # list_editable = ('state',)
    # search_fields = ('first_name', 'last_name', 'group', 'current_project__name_of_project')
    sortable_by = ('last_name', 'study_group')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectReport, ProjectReportAdmin)
