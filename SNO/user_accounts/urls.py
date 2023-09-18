from django.urls import path

from . import views


app_name = "user_accounts"

urlpatterns = [
    path('link/vk/', views.LinkVkView.as_view(), name='link_vk'),
    path('signup/vk/<int:vk_id>', views.SignupWithVKView.as_view(), name='signup_vk'),
    path('signup/vk/complete', views.SignupWithVKView.as_view(), name='signup_vk_complete'),
    path('login/vk/', views.LoginWithVKView.as_view(), name='login_vk'),

    #path('accounts/user/<int:user_id>', UserPage.as_view(), name='user'), TODO: add UserView class
    #path('accounts/user/<int:user_id>', UserPage.as_view(), name='user'), TODO: add UserUpdate class
    #path('accounts/user/<int:user_id>', UserPage.as_view(), name='user'), TODO: add UserDelete class
]