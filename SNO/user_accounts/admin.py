from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import StudyGroup, CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username','first_name', 'last_name', 'study_group')
    list_display_links = ('username','first_name', 'last_name', 'study_group')
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


admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
