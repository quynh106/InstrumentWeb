from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ADMIN PANEL (custom dashboard)
    path('manage/', include('adminpanel.urls')),
    # STORE
    path('', include('products.urls')),

    # USER ACCOUNT
    path('account/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
