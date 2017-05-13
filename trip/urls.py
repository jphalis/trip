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


admin.site.site_header = "TRIP Administration"
admin.site.site_title = "TRIP Administration"
admin.site.index_title = "TRIP"


urlpatterns = [
    # ADMIN
    url(
        r'^hidden/secure/trip/admin/',
        include(admin.site.urls)
    ),

    # GENERAL
    url(
        regex=r'^$',
        view=views.home,
        name='home'
    ),

    # ACCOUNTS
    url(
        r'^accounts/',
        include('accounts.urls', namespace='accounts')
    ),

    # AUTHENTICATION
    url(
        r'^auth/',
        include('authentication.urls', namespace='authentication')
    ),

    # BILLING
    url(
        r'^billing/',
        include('billing.urls', namespace='billing')
    ),

    # CONTACT
    url(
        r'^contact/',
        include('contact.urls', namespace='contact')
    ),

    # EVENTS
    url(
        r'^events/',
        include('events.urls', namespace='events')
    ),

    # SPONSORS
    url(
        regex=r'^sponsors/$',
        view=views.sponsors,
        name='sponsors'
    ),
]


if settings.DEBUG:
    urlpatterns += [] + static(settings.STATIC_URL,
                               document_root=settings.STATIC_ROOT)
    urlpatterns += [] + static(settings.MEDIA_URL,
                               document_root=settings.MEDIA_ROOT)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
