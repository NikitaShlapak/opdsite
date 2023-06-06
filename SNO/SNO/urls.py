from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from SNO import settings
from user_accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('events/', include('bot.urls', namespace='events')),
    path('acc/', include('user_accounts.urls', namespace='user_accounts')),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.ProfilePage.as_view(), name='profile'),
]

handler404 = "main.views.page_not_found_view"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)