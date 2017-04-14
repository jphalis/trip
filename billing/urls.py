from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'billing'


urlpatterns = [
    url(r'^checkout/(?P<event_pk>\d+)/$',
        views.checkout, name='checkout'),
    url(r'^update_auto_renew/$',
        views.update_auto_renew, name='update_auto_renew'),
]
