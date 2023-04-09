from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
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
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "study_group")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_approved",
                    "is_Free",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            "Основные данные",
            {
                "classes": ("wide",),
                "fields": ("username",'email', "password1", "password2",'first_name','last_name', 'study_group'),
            },
        ),
    )

class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('type', 'subgroup','year')
    list_display_links = ('type', 'subgroup','year')
    sortable_by = ('type', 'subgroup','year')

admin.site.register(Applications, ApplicationsAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectReport, ProjectReportAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)