from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'contact'


urlpatterns = [
    url(r'^$',
        views.inquiry, name='inquiry'),
    url(r'^unsubscribe/(?P<email>\w+|[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        views.unsubscribe, name='unsubscribe')
]
