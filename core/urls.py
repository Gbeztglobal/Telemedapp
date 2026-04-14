from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('consultations/', include('apps.consultations.urls')),
    path('diagnosis/', include('apps.diagnosis.urls')),
    path('chat/', include('apps.messaging.urls')),
    path('messaging/', include('apps.messaging.urls')),
    path('notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
