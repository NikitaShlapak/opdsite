from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from SNO import settings
from game.views import main

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('secret_game', main)
]

handler404 = "main.views.page_not_found_view"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)