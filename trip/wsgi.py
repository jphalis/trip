"""
WSGI config for trip project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import dotenv
import os

from django.core.wsgi import get_wsgi_application
from django.conf import settings

dotenv.read_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trip.settings")

if not settings.DEBUG and not settings.USING_S3:
    try:
        from dj_static import Cling
        application = Cling(get_wsgi_application())
    except StandardError:
        pass
else:
    application = get_wsgi_application()
