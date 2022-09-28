from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Vertex'
admin.site.index_title = 'Vertex'
admin.site.site_title = 'Vertex'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),

    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),

    path('api/account/', include('root.modules.accounts.urls')),
    path('api/problems/', include('root.modules.problems.urls')),
]
