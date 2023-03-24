from django.contrib import admin
from .models import *

class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'secondname', 'group', 'current_project', 'state')
    list_display_links = ('firstname', 'secondname', 'group')
    list_editable = ('state', )
    search_fields = ('firstname', 'secondname', 'group', 'current_project__name_of_project')
    sortable_by = ('secondname', 'group', 'state', 'current_project')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name_of_project', 'manager', 'project_type', 'project_status', 'edition_key')
    list_display_links = ('name_of_project',)
    list_editable = ('project_status', )
    search_fields = ('name_of_project', 'manager__firstname', 'manager__secondname')
    sortable_by = ('name_of_project', 'project_type', 'project_status')

class ProjectReportAdmin(admin.ModelAdmin):
    list_display = ('publishing_time', 'parent_project', 'heading', 'author', 'text')
    list_display_links = ('heading','publishing_time')
    search_fields = ('parent_project', 'author', 'text')
    sortable_by = ('publishing_time','parent_project','author')

admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectReport, ProjectReportAdmin)
