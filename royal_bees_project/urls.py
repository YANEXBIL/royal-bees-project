# royal_bees_project/urls.py
from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported
from django.conf import settings # Add this if you need to serve media/static
from django.conf.urls.static import static # Add this for media/static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),    
    path('results/', include('results.urls')),
    # Add any other top-level app includes here
]

# FOR DEVELOPMENT ONLY: Serve media and static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # NO EXTRA PARENTHESIS HERE