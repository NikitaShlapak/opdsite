from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *



class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('user', 'project')
    list_display_links = list_display
    search_fields = list_display
    sortable_by = list_display

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name_of_project', 'manager', 'project_type', 'project_status')
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
    list_display_links = ('username','first_name', 'last_name', 'study_group')
    # list_editable = ('state',)
    # search_fields = ('first_name', 'last_name', 'group', 'current_project__name_of_project')
    sortable_by = ('first_name','last_name', 'study_group')

class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('type', 'subgroup','year')
    list_display_links = ('type', 'subgroup','year')
    sortable_by = ('type', 'subgroup','year')

admin.site.register(Applications, ApplicationsAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectReport, ProjectReportAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)