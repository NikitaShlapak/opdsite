from django.urls import path

from . import views


app_name = "user_accounts"

urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),

    path('profile/', views.ProfilePage.as_view(), name='profile'),
    #path('accounts/user/<int:user_id>', UserPage.as_view(), name='user'), TODO: add UserView class
    #path('accounts/user/<int:user_id>', UserPage.as_view(), name='user'), TODO: add UserUpdate class
    #path('accounts/user/<int:user_id>', UserPage.as_view(), name='user'), TODO: add UserDelete class
]