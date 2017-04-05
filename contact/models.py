from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class SubscriptionManager(models.Manager):
    def subscribed(self):
        """
        Returns all active sponsors.
        """
        return super(SubscriptionManager, self).get_queryset().filter(
            is_subscribed=True)


@python_2_unicode_compatible
class Subscription(models.Model):
    email = models.EmailField(max_length=120, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    is_subscribed = models.BooleanField(default=True)

    objects = SubscriptionManager()

    class Meta:
        app_label = 'contact'
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')

    def __str__(self):
        return u"{}".format(self.email)
