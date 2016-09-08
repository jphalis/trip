from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'events'


urlpatterns = [
    url(r'^events/$',
        views.event_list,
        name='event_list'),
    url(r'^(?P<event_pk>\d+)/$',
        views.event_detail,
        name='event_detail'),
]
