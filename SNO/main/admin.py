from django.contrib import admin, messages

from django.utils.safestring import mark_safe
from django.utils.translation import ngettext

from .models import *

class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'secondname', 'group', 'current_project', 'state')
    list_display_links = ('firstname', 'secondname', 'group')
    list_editable = ('state', )
    search_fields = ('firstname', 'secondname', 'group', 'current_project__name_of_project')
    sortable_by = ('secondname', 'group', 'state', 'current_project')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name_of_project', 'manager', 'project_type', 'project_status')
    list_display_links = ('name_of_project',)
    list_editable = ('project_status',)
    search_fields = ('name_of_project', 'manager__firstname', 'manager__secondname')
    sortable_by = ('name_of_project', 'project_type', 'project_status')
    fieldsets = (
        ('Основное',
         {"fields": ("name_of_project", "get_html_poster", 'poster')}
         ),
        ("Администрирование",
         {"fields": (
         "manager", "project_status", "project_type", 'implementation_period', 'target_groups', 'edition_key')}
         ),
        ("Данные о проекте",
         {"fields": ("short_project_description", "long_project_description")}
         )
    )
    readonly_fields = ('edition_key', 'get_html_poster')

    def get_html_poster(self, object):
        return mark_safe(f"<img src={object.poster.url} height=400>")

    get_html_poster.short_description = "Постер (превью)"

    actions = ['confirm_projects']

    @admin.action(description='Одобрить проекты')
    def confirm_projects(self, request, queryset):
        updated = queryset.update(project_status=Project.ProjectStatus.ENROLLMENTOPENED)
        self.message_user(request, ngettext(
            '%d проект был успешно одобрен.',
            '%d проектов было успешно одобрено.',
            updated,
        ) % updated, messages.SUCCESS)
class ProjectReportAdmin(admin.ModelAdmin):
    list_display = ('publishing_time', 'parent_project', 'heading', 'author', 'text')
    list_display_links = ('heading','publishing_time')
    search_fields = ('parent_project', 'author', 'text')
    sortable_by = ('publishing_time','parent_project','author')

admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectReport, ProjectReportAdmin)
