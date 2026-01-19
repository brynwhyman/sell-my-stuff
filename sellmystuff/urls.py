"""
URL configuration for Sell My Stuff project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]

# Serve media files in both development and production
# Note: For production at scale, use a CDN or separate web server
# For free tier testing on Render, serving directly from Django is acceptable
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
