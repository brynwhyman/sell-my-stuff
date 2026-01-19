"""
URL configuration for Sell My Stuff project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]

# Serve media files in both development and production
# Note: For production at scale, use a CDN or separate web server
# For free tier testing on Render, serving directly from Django is acceptable
if settings.DEBUG:
    # Use static() helper in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Use serve view in production for more reliable file serving
    media_root = os.path.abspath(str(settings.MEDIA_ROOT))
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': media_root}),
    ]
