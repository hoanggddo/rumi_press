"""
URL configuration for rumi_press project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# rumi_press/rumi_press/urls.py
from django.contrib import admin
from django.urls import path, include
from tracker import views  # Import views from the tracker app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tracker/', include('tracker.urls')),  # Include URLs from the tracker app
    path('', views.index, name='index'),  # Add this line to handle the root URL
    path('accounts/', include('allauth.urls')),  # Include URLs for django-allauth
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
