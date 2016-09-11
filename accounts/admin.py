from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _

from .forms import MyUserChangeForm, MyUserCreationForm
from .models import MyUser

# Register your models here.


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    list_display = ('id', '__str__', 'is_superuser', 'is_staff',)
    list_display_links = ('id', '__str__',)
    list_filter = ('is_active', 'is_staff', 'is_superuser',
                   'date_joined', 'modified',)
    fieldsets = (
        (None,
            {'fields': ('email', 'password',)}),
        ('Basic information',
            {'fields': ('name', 'logo',)}),
        ('Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser',
                        'user_permissions')}),
        (_('Dates'),
            {'fields': ('date_joined', 'last_login', 'modified',)}),
    )
    add_fieldsets = (
        (None,
            {'classes': ('wide',),
             'fields': ('email', 'name', 'password1', 'password2',)}),
    )
    readonly_fields = ('date_joined', 'last_login', 'modified',)
    search_fields = ('id', 'email', 'name',)
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


admin.site.unregister(Group)
admin.site.register(MyUser, MyUserAdmin)
