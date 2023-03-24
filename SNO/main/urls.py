from django.urls import path
from . import views

urlpatterns = [
    path('', views.Main, name='MAIN'),
    path('<str:type>_projects', views.MainFiltered, name='filter_projects'),
    path('OPD/', views.Opd, name='OPD'),
    path('project/<int:project_id>/', views.ProjectPage, name='project'),
    path('info/', views.Info, name='info'),
    path('project/<int:project_id>/add_report', views.AddReport, name='add_report'),
    path('project/add', views.AddProject, name='add_project'),
    path('register', views.AddTeamMember, name='add_user'),
    path('project/<int:project_id>/register', views.ExpandTeam, name='expand'),
    path('project/<int:project_id>/confirm', views.verify_edition, name='verify_edition'),
    path('project/<int:project_id>/reject', views.reject_project, name='verify_delete'),
    path('project/<int:pk>/edit/<int:edition_key>', views.ProjectUpdateView.as_view(), name='edit'),
    path('project/<int:project_id>/<int:student_id>/apply', views.confirm_app, name='apply'),
    path('project/<int:project_id>/<int:student_id>/decline', views.decline_app, name='decline')
]