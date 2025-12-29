"""
URL configuration for GerenciadorDeTarefas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home import views as home_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home_views.landing_page, name="home"),
    path('creditos/', home_views.creditos, name="creditos"),
    path('sobre/', home_views.sobre, name="sobre"),
    path('api/versao/', home_views.versao_info, name="versao"),
    path('blog/', home_views.blog, name="blog"),
    path('tarefas/', include('tasks.urls')),
    path('comentarios/', include('comentarios.urls')),
    path('notifications/', include('django_nyt.urls')),
    path('wiki/', include('wiki.urls')),
]
# Isso permite que o Django sirva os arquivos de mídia (imagens da wiki) durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
