from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Event

# Register your models here.


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
    readonly_fields = ('created', 'modified',)
    search_fields = ('name', 'sponsors__name', 'sponsors__email',
                     'attendees__first_name', 'attendees_last_name',
                     'attendees__email',)
    actions = ('enable', 'disable',)

    class Meta:
        model = Event

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


admin.site.register(Event, EventAdmin)
