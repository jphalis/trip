from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Attendee, Event
from .utils import send_event_email

# Register your models here.


class AttendeeAdmin(admin.ModelAdmin):
    # Add which event they are registered for - KnobLinx code
    list_display = ('id', 'email', 'full_name', 'event_name',)
    list_display_links = ('id', 'email',)
    list_filter = ('created', 'modified',)
    fieldsets = (
        (None,
            {'fields': ('email', 'first_name', 'last_name',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('email', 'last_name',)

    class Meta:
        model = Attendee


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
                        'member_fee', 'non_member_fee', 'sponsors',
                        'attendees',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)  # add attendees
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
                'event_name': obj.name,
                'event_start_date': obj.start_date,
                'event_end_date': obj.end_date,
                'event_pk': obj.pk,
                'event_member_fee': obj.member_fee,
                'event_non_member_fee': obj.non_member_fee,
                'event_description': obj.description
            })
        else:
            obj.save()
        return obj

    def send_email_to_list(self, request, queryset):
        """
        Sends an email about the event to the mailing list.
        """
        for event in queryset:
            send_event_email({
                'event_name': event.name,
                'event_start_date': event.start_date,
                'event_end_date': event.end_date,
                'event_pk': event.pk,
                'event_member_fee': event.member_fee,
                'event_non_member_fee': event.non_member_fee,
                'event_description': event.description
            })
    send_email_to_list.short_description = _("Send event email")

    def enable(self, request, queryset):
        """
        Updates is_active to be True.
        """
        queryset.update(is_active=True)
    enable.short_description = _("Make events public")

    def disable(self, request, queryset):
        """
        Updates is_active to be False.
        """
        queryset.update(is_active=False)
    disable.short_description = _("Disable events")


admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(Event, EventAdmin)
