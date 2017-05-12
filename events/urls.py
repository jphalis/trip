from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'events'


urlpatterns = [
    url(
        regex=r'^(?P<event_pk>\d+)/$',
        view=views.detail,
        name='detail'
    ),
    url(
        regex=r'^(?P<event_pk>\d+)/success/$',
        view=views.reg_success,
        name='reg_success'
    ),
    url(
        regex=r'^$',
        view=views.list,
        name='list'
    ),
]
