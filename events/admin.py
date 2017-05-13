from django.conf import settings
from django.contrib import admin, messages
from django.utils.translation import ugettext as _

from .models import Event
from .utils import send_event_email

# Register your models here.


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_date', 'end_date',
                    'sponsor_count', 'attendee_count', 'is_active',)
    list_display_links = ('id', 'name',)
    list_filter = ('start_date', 'end_date', 'created', 'modified',
                   'is_active',)
    raw_id_fields = ['sponsors', 'attendees']
    fieldsets = (
        (None,
            {'fields': ('name', 'start_date', 'end_date', 'description',
                        'email_description', 'member_fee', 'non_member_fee',
                        'sponsors', 'attendees',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified', 'attendees',)
    search_fields = ('name', 'sponsors__name', 'sponsors__email',
                     'attendees__first_name', 'attendees_last_name',
                     'attendees__email',)
    actions = ('send_email_to_list', 'enable', 'disable',)

    class Meta:
        model = Event

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.save()
            # send email about new event
            send_event_email({
                'protocol': 'https' if request.is_secure() else 'http',
                'domain': request.get_host(),
                'event_name': obj.name,
                'event_start_date': obj.event_start_date,
                'event_end_date': obj.event_end_date,
                'event_pk': obj.pk,
                'event_member_fee': obj.member_fee,
                'event_non_member_fee': obj.non_member_fee,
                'event_email_description': obj.email_description,
                'event_sponsors': obj.get_sponsors_info,
                'event_url': obj.get_absolute_url,
                'contact_email': settings.DEFAULT_HR_EMAIL
            })
        else:
            obj.save()
        return obj

    def send_email_to_list(self, request, queryset):
        """Sends an email about the event to the mailing list."""
        for obj in queryset:
            send_event_email({
                'protocol': 'https' if request.is_secure() else 'http',
                'domain': request.get_host(),
                'event_name': obj.name,
                'event_start_date': obj.event_start_date,
                'event_end_date': obj.event_end_date,
                'event_pk': obj.pk,
                'event_member_fee': obj.member_fee,
                'event_non_member_fee': obj.non_member_fee,
                'event_email_description': obj.email_description,
                'event_sponsors': obj.get_sponsors_info,
                'event_url': obj.get_absolute_url,
                'contact_email': settings.DEFAULT_HR_EMAIL
            })
        messages.add_message(
            request, messages.SUCCESS, _('Emails have been sent.'))
    send_email_to_list.short_description = _("Send event email")

    def enable(self, request, queryset):
        """Updates is_active to be True."""
        queryset.update(is_active=True)
        messages.add_message(
            request, messages.SUCCESS, _('Events have been enabled.'))
    enable.short_description = _("Make events public")

    def disable(self, request, queryset):
        """Updates is_active to be False."""
        queryset.update(is_active=False)
        messages.add_message(
            request, messages.SUCCESS, _('Events have been disabled.'))
    disable.short_description = _("Disable events")
