from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import StudyGroup, CustomUser, VKTokenConnection


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username','first_name', 'last_name', 'study_group')
    list_display_links = ('username','first_name', 'last_name', 'study_group')
    sortable_by = ('first_name','last_name', 'study_group')
    fieldsets = (
        ('Учётная запись', {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "study_group")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_approved",
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
    def get_str(self, object):
        return f"{object.__str__()}"

    get_str.short_description = "Полное название"

    list_display = ('get_str','type', 'year')
    list_display_links = ('get_str',)
    sortable_by = ('get_str','type', 'year')
    readonly_fields = ('get_str',)

    fieldsets = (
        ('Основное', {"fields": ("get_str",'related_teacher')}),
        ("Данные о группе", {"fields": ("type", "subgroup", "year")}),
    )

class VKTokenConnectionAdmin(admin.ModelAdmin):
    list_display = ('email','user_id', 'expires_in', 'dt_created')
    list_display_links = ('email', 'user_id')

    readonly_fields = ('access_token'    , 'expires_in' , 'dt_created')

    fieldsets = (
        ('Основная информация', {"fields": ("email", "user_id", 'access_token')}),
        ('Даты', {'fields':( 'expires_in', 'dt_created')} )
    )

admin.site.register(VKTokenConnection,VKTokenConnectionAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
