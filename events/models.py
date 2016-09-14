from __future__ import unicode_literals

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel

# Create your models here.


def image_upload_loc(instance, filename):
    """
    Stores the company logo in <company_name>/logos/filename.
    """
    return "{0}/images/{1}".format(instance.name, filename)


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
            .order_by('start_date')[:num_returned]

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
    start_date = models.DateTimeField(verbose_name='Start of Event')
    end_date = models.DateTimeField(verbose_name='End of Event')
    image = models.ImageField(_('event image'),
                              upload_to=image_upload_loc,
                              blank=True,
                              help_text='''Please upload an image with
                               sizes: (W - 750px | H - 300px).''')
    description = models.TextField(max_length=2000, blank=True)
    sponsors = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                      related_name='event_sponsors',
                                      blank=True,
                                      help_text='''Select the magnifying glass
                                       to add sponsors.''')

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
        return reverse('events:detail', kwargs={"event_pk": self.pk})

    @property
    def event_status(self):
        now = datetime.now()
        start = self.start_date
        if start <= now and self.end_date >= now:
            return "Happening now"
        elif start >= now:
            return "Upcoming"
        return "Completed"

    @property
    def event_image(self):
        """
        Returns the logo of the user. If there is no logo,
        a default one will be rendered.
        """
        if self.image:
            return "{0}{1}".format(settings.MEDIA_URL, self.image)
        return settings.STATIC_URL + 'img/default-company-logo.jpg'

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
        return self.sponsors.values('id', 'name', 'logo',)

    @property
    def sponsor_count(self):
        """
        Returns the number of applicants for the job.
        """
        return self.get_sponsors_info.count()
