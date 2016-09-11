from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'accounts'


urlpatterns = [
    url(r"^authenticate/$",
        views.auth_base_view,
        name="auth_base_view"),
    url(r"^authenticate/complete/$",
        views.auth_login_register,
        name="auth_login_register"),
    url(r"^logout/$",
        views.auth_logout,
        name="auth_logout"),
    url(r"^settings/$",
        views.account_settings,
        name="account_settings"),
    url(r"^password/reset/$",
        views.password_reset,
        name="password_reset"),
    url(r"^password/reset/confirm/"
        r"(?P<uidb64>[0-9A-Za-z_\-]+)/"
        r"(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.password_reset_confirm,
        name="password_reset_confirm"),
    url(r'^(?P<user_pk>\d+)/$',
        views.detail,
        name='detail'),
]
