from django.contrib import admin
from .models import *

class EventAdmin(admin.ModelAdmin):
    list_display = ('publishing_time', 'title', 'act_time', 'deadline', )
    list_display_links = ('publishing_time', 'title', 'act_time', 'deadline',)
    search_fields = ('title', )
    sortable_by = ('publishing_time', 'title', 'act_time', 'deadline',)

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('data','event', 'time'  )
    list_display_links = list_display
    search_fields = ('data','event', )
    sortable_by = list_display



admin.site.register(Event, EventAdmin)
admin.site.register(Application, ApplicationAdmin)