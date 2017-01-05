from __future__ import unicode_literals

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel
from .signals import membership_dates_update

# Create your models here.


class MembershipManager(models.Manager):
    def create(self, user, billing_fee, **extra_fields):
        """
        Creates a membership.
        """
        if not user:
            raise ValueError('Memberships must have a user.')
        elif not billing_fee:
            raise ValueError('Memberships must have a billing fee.')

        membership = self.model(user=user,
                                billing_fee=Decimal(str(billing_fee)),
                                **extra_fields)
        membership.save(using=self._db)
        return membership


@python_2_unicode_compatible
class Membership(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    auto_renew = models.BooleanField(default=True)
    billing_fee = models.DecimalField(_('next billing fee'), max_digits=8,
                                      decimal_places=2,
                                      validators=[MinValueValidator(0.0)])

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(default=timezone.now() + timedelta(days=365))

    objects = MembershipManager()

    class Meta:
        app_label = 'billing'
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')

    def __str__(self):
        return str(self.user.get_full_name)

    def update_status(self):
        _user = self.user
        _user.is_active = True if self.end_date >= timezone.now() else False
        _user.save()


def update_membership_status(sender, instance, created, **kwargs):
    if not created:
        instance.update_status()


post_save.connect(update_membership_status, sender=Membership)


def update_membership_dates(sender, new_start_date, **kwargs):
    membership = sender
    current_end_date = membership.end_date

    if current_end_date >= new_start_date:
        #append new_start date plus offset to date end of the instance
        membership.end_date = current_end_date + timedelta(days=365)
    else:
        #set a new start date and new end date with the same offset.
        membership.start_date = new_start_date
        membership.end_date = new_start_date + timedelta(days=365)

    membership.save()


membership_dates_update.connect(update_membership_dates)
