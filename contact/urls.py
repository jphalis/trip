from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'contact'


urlpatterns = [
    url(r"^$", views.inquiry, name="inquiry"),
]
