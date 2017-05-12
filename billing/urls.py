from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'billing'


urlpatterns = [
    url(
        regex=r'^checkout/(?P<event_pk>\d+)/$',
        view=views.checkout,
        name='checkout'
    ),
    url(
        regex=r'^update_auto_renew/$',
        view=views.update_auto_renew,
        name='update_auto_renew'
    ),
]
