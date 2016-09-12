"""
WSGI config for trip project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trip.settings")

application = get_wsgi_application()

if not settings.DEBUG and not settings.USING_S3:
    try:
        from dj_static import Cling, MediaCling
        application = Cling(MediaCling(get_wsgi_application()))
    except:
        pass
