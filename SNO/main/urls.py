from django.urls import path
from . import views
from .views import ConfirmOrDeclineApplication, ProjectUpdateView, \
    CreateApplication, ProjectView, ProjectCreationView, RejectProjectView,  \
    SetProjectStatusView

urlpatterns = [
    path('', views.Main, name='MAIN'),
    path('<str:type>_projects/', views.MainFiltered, name='filter_projects'),

    path('info/', views.Info, name='info'),

    path('project/add/', ProjectCreationView.as_view(), name='add_project'),
    path('project/<int:project_id>/', ProjectView.as_view(), name='project'),
    path('project/<int:project_id>/edit/', ProjectUpdateView.as_view(), name='edit'),
    path('project/<int:project_id>/reject/', RejectProjectView.as_view(), name='verify_delete'),
    path('project/<int:project_id>/act:<str:action>/', SetProjectStatusView.as_view(), name='set_project_status'),

    path('project/<int:project_id>/register/', CreateApplication.as_view(), name='expand'),
    path('project/<int:app_id>/<str:action>/', ConfirmOrDeclineApplication.as_view(), name='apply_or_decline'),

    path('project/<int:project_id>/add_report/', views.AddReport, name='add_report'),


]