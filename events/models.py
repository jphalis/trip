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
    def create(self, name, date, image=None, **extra_fields):
        """
        Creates an event.
        """
        if not name:
            raise ValueError('The event must have a name.')
        elif not date:
            raise ValueError('The event must have a date.')

        event = self.model(name=name, date=date, image=image, **extra_fields)
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
            .filter(is_active=True, date__gte=timezone.now()) \
            .prefetch_related('sponsors') \
            .order_by('date')[:num_returned]

    def own(self, user):
        """
        Returns all events the user is sponsoring.
        """
        return super(EventManager, self).get_queryset() \
            .filter(sponsors=user) \
            .prefetch_related('sponsors') \
            .order_by('date')


@python_2_unicode_compatible
class Event(TimeStampedModel):
    name = models.CharField(max_length=120)
    date = models.DateTimeField(verbose_name='Date of Event')
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
        if self.date >= datetime.now():
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
        d = self.date
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
