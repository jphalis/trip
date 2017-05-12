from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'accounts'


urlpatterns = [
    url(
        regex=r"^memberships/$",
        view=views.memberships,
        name="memberships"
    ),
    url(
        regex=r"^settings/$",
        view=views.account_settings,
        name="account_settings"
    ),
    url(
        regex=r'^(?P<sponsor_pk>\d+)/$',
        view=views.detail,
        name='detail'
    ),
]
