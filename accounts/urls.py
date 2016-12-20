from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'accounts'


urlpatterns = [
    url(r"^memberships/$",
        views.memberships,
        name="memberships"),
    url(r"^settings/$",
        views.account_settings,
        name="account_settings"),
    url(r'^(?P<sponsor_pk>\d+)/$',
        views.detail,
        name='detail'),
]
