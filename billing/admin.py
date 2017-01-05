from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Membership

# Register your models here.


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'start_date', 'end_date',)
    list_display_links = ('id', '__str__',)
    list_filter = ('created', 'modified',)
    fieldsets = (
        (None,
            {'fields': ('user', 'auto_renew', 'billing_fee',)}),
        (_('Dates'),
            {'fields': ('start_date', 'end_date', 'created', 'modified',)}),
    )
    readonly_fields = ('start_date', 'created', 'modified',)
    search_fields = ('user__first_name', 'user_last_name', 'user__email',)

    class Meta:
        model = Membership


admin.site.register(Membership, MembershipAdmin)
