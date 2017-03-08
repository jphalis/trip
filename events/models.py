from __future__ import unicode_literals

from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from accounts.models import Sponsor
from core.models import TimeStampedModel

# Create your models here.


class Attendee(TimeStampedModel):
    email = models.EmailField(max_length=120)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    class Meta:
        app_label = 'events'
        verbose_name = _('attendee')
        verbose_name_plural = _('attendees')

    def __str__(self):
        return str(self.email)

    @cached_property
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return "{0} {1}".format(self.first_name, self.last_name)


class EventManager(models.Manager):
    def create(self, name, start_date, end_date, image=None, **extra_fields):
        """
        Creates an event.
        """
        if not name:
            raise ValueError('The event must have a name.')
        elif not start_date:
            raise ValueError('The event must have a start date.')
        elif not end_date:
            raise ValueError('The event must have a end date.')

        event = self.model(name=name, start_date=start_date, end_date=end_date,
                           image=image, **extra_fields)
        event.save(using=self._db)
        return event

    def active(self):
        """
        Returns all active events.
        """
        return super(EventManager, self).get_queryset() \
            .filter(is_active=True) \
            .prefetch_related('sponsors')

    def featured(self, num_returned=None):
        """
        Returns all featured events.
        Featured events are ordered by closest to their date.
        """
        return super(EventManager, self).get_queryset() \
            .filter(is_active=True, end_date__gte=timezone.now()) \
            .prefetch_related('sponsors') \
            .order_by('start_date', 'end_date')[:num_returned]

    def own(self, user):
        """
        Returns all events the user is sponsoring.
        """
        return super(EventManager, self).get_queryset() \
            .filter(sponsors=user) \
            .prefetch_related('sponsors') \
            .order_by('start_date')


@python_2_unicode_compatible
class Event(TimeStampedModel):
    name = models.CharField(max_length=120)
    description = models.TextField(max_length=2000, blank=True,
                                   help_text='You may use HTML when rendering')
    member_fee = models.PositiveIntegerField(_('member fee'),
                                             help_text='Value in cents.')
    non_member_fee = models.PositiveIntegerField(_('non-member fee'),
                                                 help_text='Value in cents.')
    sponsors = models.ManyToManyField(Sponsor, related_name='event_sponsors',
                                      blank=True)
    attendees = models.ManyToManyField(Attendee, related_name='event_attendees',
                                       blank=True)

    start_date = models.DateTimeField(_('start date of event'))
    end_date = models.DateTimeField(_('end date of event'))

    is_active = models.BooleanField(default=True)

    objects = EventManager()

    class Meta:
        app_label = 'events'
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def __str__(self):
        return u'{0}'.format(self.name)

    def get_absolute_url(self):
        """
        Returns the url for the event.
        """
        return reverse('events:detail', kwargs={'event_pk': self.pk})

    def get_reg_success_url(self):
        """
        Returns the url for an event after being successfully registered.
        """
        return reverse('events:reg_success', kwargs={'event_pk': self.pk})

    def get_checkout_url(self):
        """
        Returns the checkout url for an event.
        """
        return reverse('billing:checkout', kwargs={'event_pk': self.pk})

    @property
    def event_status(self):
        now = datetime.now()
        start = self.start_date
        if start <= now and self.end_date >= now:
            return "Happening now"
        elif start >= now:
            return "Upcoming"
        return "Completed"

    @cached_property
    def event_date(self):
        start = self.start_date
        end = self.end_date
        if start.date() == end.date():
            return "{0} | {1}-{2}".format(
                start.strftime("%B %d, %Y"),
                start.strftime("%I:%M %p").lstrip('0'),
                end.strftime("%I:%M %p").lstrip('0'))
        return "{0} - {1}".format(
            start.strftime("%B %d, %Y"), end.strftime("%B %d, %Y"))

    @cached_property
    def event_start_date(self):
        d = self.start_date
        # d.strftime("%A | %B %d, %Y | ") + d.strftime("%I:%M %p").lstrip('0')
        return d.strftime("%B %d, %Y | ") + d.strftime("%I:%M %p").lstrip('0')

    @cached_property
    def event_end_date(self):
        d = self.end_date
        # d.strftime("%A | %B %d, %Y | ") + d.strftime("%I:%M %p").lstrip('0')
        return d.strftime("%B %d, %Y | ") + d.strftime("%I:%M %p").lstrip('0')

    @cached_property
    def get_sponsors_info(self):
        """
        Returns the information for each sponsor of the event.
        """
        return self.sponsors.values('id', 'name', 'logo', 'website')

    @cached_property
    def get_attendees_info(self):
        """
        Returns the information for each user registered for the event.
        """
        return self.attendees.values('id', 'first_name', 'last_name')

    @property
    def sponsor_count(self):
        """
        Returns the number of sponsors for the event..
        """
        return self.get_sponsors_info.count()

    @property
    def attendee_count(self):
        """
        Returns the number of attendees of the event.
        """
        return self.get_attendees_info.count()
