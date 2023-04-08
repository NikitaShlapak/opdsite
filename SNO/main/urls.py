from django.urls import path
from . import views
from .views import RegisterUser, ConfirmOrDeclineApplication, LoginUser, ProfilePage, ProjectUpdateView, \
    CreateApplication, ProjectView, ProjectCreationView

urlpatterns = [
    path('', views.Main, name='MAIN'),
    path('<str:type>_projects', views.MainFiltered, name='filter_projects'),

    path('info/', views.Info, name='info'),

    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('accounts/profile/', ProfilePage.as_view(), name='profile'),
    #path('accounts/user/<int:user_id>', UserPage.as_view(), name='user'), TODO: add UserPage class

    path('project/<int:project_id>/', ProjectView.as_view(), name='project'),
    path('project/add', ProjectCreationView.as_view(), name='add_project'),
    path('project/<int:pk>/edit/<int:edition_key>', ProjectUpdateView.as_view(), name='edit'),
    path('project/<int:project_id>/register', CreateApplication.as_view(), name='expand'),
    path('project/<int:project_id>/confirm', views.verify_edition, name='verify_edition'),
    path('project/<int:project_id>/reject', views.reject_project, name='verify_delete'),



    path('project/<int:app_id>/<str:action>/', ConfirmOrDeclineApplication.as_view(), name='apply_or_decline'),


    path('project/<int:project_id>/add_report', views.AddReport, name='add_report'),


]