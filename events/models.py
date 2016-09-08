from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from accounts.models import Sponsor
from core.models import TimeStampedModel

# Create your models here.


class EventManager(models.Manager):
    def create(self, name, date, **extra_fields):
        """
        Creates an event.
        """
        if not name:
            raise ValueError('The event must have a name.')
        elif not date:
            raise ValueError('The event must have a date.')

        event = self.model(name=name, date=date, **extra_fields)
        event.save(using=self._db)
        return event

    def active(self):
        """
        Returns all active events.
        """
        return super(EventManager, self).get_queryset() \
            .filter(is_active=True) \
            .prefetch_related('sponsors')

    def featured(self):
        """
        Returns all featured events.
        Featured events are ordered by closest to their date.
        """
        return super(EventManager, self).get_queryset() \
            .filter(is_active=True, date__lte=timezone.now()) \
            .prefetch_related('sponsors')


@python_2_unicode_compatible
class Event(TimeStampedModel):
    name = models.CharField(max_length=120)
    date = models.DateTimeField(verbose_name='Date of Event')
    sponsors = models.ManyToManyField(Sponsor, related_name='event_sponsors',
                                      blank=True)

    is_active = models.BooleanField(default=True)

    objects = EventManager()

    class Meta:
        app_label = 'events'
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ['-date']

    def __str__(self):
        return u'{0}'.format(self.name)

    def get_absolute_url(self):
        """
        Returns the url for the event.
        """
        return reverse('events:event_detail', kwargs={"event_pk": self.pk})

    @cached_property
    def get_sponsors_info(self):
        """
        Returns the information for each sponsor of the event.
        """
        return self.attendees.values('id', 'name', 'logo',)
