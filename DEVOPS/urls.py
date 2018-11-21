"""AIOO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from projects.views import (
    ExcelMiddleware, 
    Dashboard, 
    About, 
    Scheduler, 
    Login, 
    Logout, 
    Home, 
    Ajax, 
    Register, 
    CountryView,
    ProjectPost,
    ProjectUpdate,
    Kanban,
    Nodes,
    Locations
)


admin.site.site_header = "Bee Projects"
admin.site.site_title = "Bee Projects"
admin.site.index_title = "Welcome to Bee Projects"

urlpatterns = [
    path('about/', About),
    path('admin/', admin.site.urls),
    path('api/',ExcelMiddleware),
    path('dashboard/',Dashboard),
    path('calendar/<pid>/',Scheduler),
    path('login/',Login),
    path('',Login),
    path('home/',Home),
    path('logout/',Logout),
    path('register/',Register),
    path('ajax/',Ajax),
    path('post/project/new/',ProjectPost, name='post_new'),
    path('post/project/update/<id>/',ProjectUpdate, name='post_update'),
    path('project/kanban/',Kanban),
    path('project/nodes/<pid>/',Nodes),
    path('location/<pid>/',Locations)
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)