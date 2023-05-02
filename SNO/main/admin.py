from django.contrib import admin, messages

from django.utils.safestring import mark_safe
from django.utils.translation import ngettext

from .models import *


admin.AdminSite.site_title = 'OPD projects'
admin.AdminSite.site_header = 'Админ-панель сайта имени Руслана Внукова'
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('user', 'project')
    list_display_links = list_display
    search_fields = list_display
    sortable_by = list_display

    actions = ['confirm_applications']

    @admin.action(description='Одобрить заявки')
    def confirm_applications(self, request, queryset):
        added = not_added = 0
        for apply in queryset:
            try:
                apply.project.team.add(apply.user)
                apply.project.save()
            except:
                not_added=not_added + 1
            else:
                added=added + 1
                apply.delete()
        self.message_user(request,f'{len(list(queryset))} заявок было обработано. Добавлено пользователей: {added}. Не удалось добавить: {not_added}', messages.SUCCESS)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name_of_project', 'manager', 'project_type', 'project_status')
    list_display_links = ('name_of_project',)
    list_editable = ('project_status', )
    search_fields = ('name_of_project', 'manager__firstname', 'manager__secondname')
    sortable_by = ('name_of_project', 'project_type', 'project_status')
    fieldsets = (
        ('Основное',
            {"fields": ("name_of_project", "get_html_poster", 'poster')}
         ),
        ("Администрирование",
            {"fields": ("manager", "project_status", "project_type", 'implementation_period', 'target_groups','edition_key')}
         ),
        ("Данные о проекте",
            {"fields": ("short_project_description","long_project_description","team")}
         )
    )
    readonly_fields = ('edition_key','get_html_poster')
    def get_html_poster(self, object):
        return mark_safe(f"<img src={object.poster.url} height=400>")

    get_html_poster.short_description="Постер (превью)"

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
    list_display = ('parent_project', 'heading', 'author', 'text')
    list_display_links = ('heading',)
    search_fields = ('parent_project', 'author', 'text')
    sortable_by = ('parent_project','author')

class ProjectReportMarkAdmin(admin.ModelAdmin):
    list_display = ('author','related_report',   'creation_time',  'value')
    list_display_links = ('author',  'related_report')
    list_filter = ('author', 'related_report__parent_project',)
    list_editable = ('value',)

    search_fields = ('author__username','author__first_name','author__last_name', 'related_report__heading','related_report__parent_project__name_of_project')
    search_help_text = 'Введите часть логина, имени или фамилии преподавателя, названия проекта или заголовка отчёта'

    sortable_by = ('author',  'related_report__heading', 'creation_time',  'value')




admin.site.register(ProjectReportMark, ProjectReportMarkAdmin)
admin.site.register(Applications, ApplicationsAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectReport, ProjectReportAdmin)
