from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'events'


urlpatterns = [
    url(r'^(?P<event_pk>\d+)/$',
        views.detail,
        name='detail'),
    url(r'^(?P<event_pk>\d+)/success/$',
        views.reg_success,
        name='reg_success'),
    url(r'^$',
        views.list,
        name='list'),
]
