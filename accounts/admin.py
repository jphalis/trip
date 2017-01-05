from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _

from authentication.forms import MyUserCreationForm
from .forms import MyUserChangeForm
from .models import MyUser, Sponsor

# Register your models here.


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    list_display = ('id', '__str__', 'is_superuser', 'is_staff', 'is_active',)
    list_display_links = ('id', '__str__',)
    list_filter = ('is_active', 'is_staff', 'is_superuser',
                   'date_joined', 'modified',)
    fieldsets = (
        ('Basic Information',
            {'fields': ('email', 'first_name', 'last_name', 'password',)}),
        ('Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser',
                        'user_permissions')}),
        (_('Dates'),
            {'fields': ('date_joined', 'last_login', 'modified',)}),
    )
    add_fieldsets = (
        (None,
            {'classes': ('wide',),
             'fields': ('email', 'first_name', 'last_name',
                        'password1', 'password2',)}),
    )
    readonly_fields = ('date_joined', 'last_login', 'modified',)
    search_fields = ('id', 'email', 'first_name', 'last_name',)
    ordering = ('id',)
    filter_horizontal = ('user_permissions',)
    actions = ('enable', 'disable',)

    def enable(self, request, queryset):
        """
        Updates is_active to be True.
        """
        queryset.update(is_active=True)
    enable.short_description = _("Enable selected users")

    def disable(self, request, queryset):
        """
        Updates is_active to be False.
        """
        queryset.update(is_active=False)
    disable.short_description = _("Disable selected users")


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active',)
    list_display_links = ('id', 'name',)
    list_filter = ('is_active', 'created', 'modified',)
    raw_id_fields = ['affiliates']
    fieldsets = (
        (None,
            {'fields': ('name', 'logo', 'website', 'affiliates', )}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('name', 'website', 'name', 'affiliates__get_full_name',
                     'affiliates__email',)
    actions = ('enable', 'disable',)

    class Meta:
        model = Sponsor

    def enable(self, request, queryset):
        """
        Updates is_active to be True.
        """
        queryset.update(is_active=True)
    enable.short_description = _("Enable selected sponsors")

    def disable(self, request, queryset):
        """
        Updates is_active to be False.
        """
        queryset.update(is_active=False)
    disable.short_description = _("Disable selected sponsors")


admin.site.unregister(Group)
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Sponsor, SponsorAdmin)
