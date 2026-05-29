"""
VIBE Social Media - Main URL Configuration
==========================================
Routes all incoming requests to the correct views.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel (default)
    path('django-admin/', admin.site.urls),

    # Our main app URLs
    path('', include('vibe_app.urls')),

    # Authentication (allauth for Google login)
    path('accounts/', include('allauth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
