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
# Convert MEDIA_ROOT to absolute string path (required for static() function)
import os
media_root_path = os.path.abspath(str(settings.MEDIA_ROOT))
urlpatterns += static(settings.MEDIA_URL, document_root=media_root_path)
