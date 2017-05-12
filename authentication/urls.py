from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'authentication'


urlpatterns = [
    url(
        regex=r"^login/$",
        view=views.auth_base_view,
        name="auth_base_view"
    ),
    url(
        regex=r"^login/complete/$",
        view=views.auth_login,
        name="auth_login"
    ),
    url(
        regex=r"^memberships/register/$",
        view=views.auth_register,
        name="auth_register"
    ),
    url(
        regex=r"^logout/$",
        view=views.auth_logout,
        name="auth_logout"
    ),
    url(
        regex=r"^password/forgot/$",
        view=views.password_reset,
        name="password_reset"
    ),
    url(
        regex=r"^password/reset/confirm/"
              r"(?P<uidb64>[0-9A-Za-z_\-]+)/"
              r"(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        view=views.password_reset_confirm,
        name="password_reset_confirm"
    ),
]
