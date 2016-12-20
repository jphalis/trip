"""Trip URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from . import views


admin.site.site_header = "Trip Administration"
admin.site.index_title = "Trip"


urlpatterns = [
    # ADMIN
    url(r'^hidden/secure/trip/admin/',
        include(admin.site.urls)),

    # SUMMERNOTE - WSGIEditor
    url(r'^summernote/',
        include('django_summernote.urls')),

    # GENERAL
    url(r'^$',
        views.home, name='home'),

    # ACCOUNTS
    url(r'^accounts/',
        include('accounts.urls', namespace='accounts')),

    # AUTHENTICATION
    url(r'^auth/',
        include('authentication.urls', namespace='authentication')),

    # CONTACT
    url(r'^contact/',
        include('contact.urls', namespace='contact')),

    # EVENTS
    url(r'^events/',
        include('events.urls', namespace='events')),

    # SPONSORS
    url(r'^sponsors/$',
        views.sponsors, name='sponsors'),
]


if settings.DEBUG:
    urlpatterns += [] + static(settings.STATIC_URL,
                               document_root=settings.STATIC_ROOT)
    urlpatterns += [] + static(settings.MEDIA_URL,
                               document_root=settings.MEDIA_ROOT)
