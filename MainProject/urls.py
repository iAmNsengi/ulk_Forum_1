from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from MainApp.views import SearchResultsList

urlpatterns = [
    path('post/search/',SearchResultsList.as_view(),name='search'),
    path('',include('MainApp.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^froala_editor/', include('froala_editor.urls')),  

    path('chat/', include('rooms.urls')),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
