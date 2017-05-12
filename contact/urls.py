from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'contact'


urlpatterns = [
    url(
        regex=r'^$',
        view=views.inquiry,
        name='inquiry'
    ),
    url(
        regex=r"^unsubscribe/"
              r"(?P<email>\w+|[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$",
        view=views.unsubscribe,
        name='unsubscribe'
    )
]
