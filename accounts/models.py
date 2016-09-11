from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

# Create your models here.


def logo_upload_loc(instance, filename):
    """
    Stores the company logo in <company_name>/logos/filename.
    """
    return "{0}/logos/{1}".format(instance.name, filename)


class MyUserManager(BaseUserManager):
    def _create_user(self, email, name, password, is_staff, is_superuser,
                     **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()

        if not email:
            raise ValueError('Users must have an email.')

        user = self.model(email=self.normalize_email(email), name=name,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra_fields):
        return self._create_user(email, name, password,
                                 is_staff=False, is_superuser=False,
                                 **extra_fields)

    def create_superuser(self, email, name, password, **extra_fields):
        return self._create_user(email, name, password,
                                 is_staff=True, is_superuser=True,
                                 **extra_fields)


@python_2_unicode_compatible
class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=120, unique=True)
    name = models.CharField(_('company name'), max_length=50, blank=True)
    logo = models.ImageField(_('company logo'),
                             upload_to=logo_upload_loc,
                             blank=True,
                             help_text='''Please upload an image with
                              sizes: (W - 488px | H - 150px)''')

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    modified = models.DateTimeField(_('last modified'), auto_now=True)

    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False,
                                   help_text='Allows users to create events.')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = MyUserManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Returns the url for the user.
        """
        return reverse('accounts:detail', kwargs={"user_pk": self.pk})

    @cached_property
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.name

    @cached_property
    def get_short_name(self):
        """
        Returns the first name for the user.
        """
        return self.get_full_name()

    @property
    def company_logo(self):
        """
        Returns the logo of the user. If there is no logo,
        a default one will be rendered.
        """
        if self.logo:
            return "{0}{1}".format(settings.MEDIA_URL, self.logo)
        return settings.STATIC_URL + 'img/default-company-logo.jpg'

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to the user.
        """
        send_mail(subject, message, from_email, [self.email])

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        return True

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        return True
