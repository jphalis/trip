from django.contrib import admin
from django.utils.translation import ugettext as _

from django_summernote.admin import SummernoteModelAdmin

from .models import Event

# Register your models here.


class EventAdmin(SummernoteModelAdmin):
    list_display = ('id', 'name', 'date', 'sponsor_count', 'is_active',)
    list_display_links = ('id', 'name',)
    list_filter = ('date', 'created', 'modified', 'is_active',)
    raw_id_fields = ['sponsors']
    fieldsets = (
        (None,
            {'fields': ('name', 'date', 'image', 'description', 'sponsors',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('name', 'sponsors__name', 'sponsors__email',)
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
