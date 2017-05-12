"""
Glossary of accounts/forms.py:

- Account settings form
- MyUser change form (admin only)
"""

from __future__ import unicode_literals

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = None

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .models import MyUser

# Create your forms here.


def clean_passwords(data, password1, password2):
    if password1 in data and password2 in data:
        if data[password1] != data[password2]:
            raise forms.ValidationError(
                _("You must type the same password each time."))
        validate_password(data[password2])
    return data[password2]


class AccountSettingsForm(forms.ModelForm):
    """
    A form used for users to update their account
    information.
    """
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(),
        max_length=120
    )
    first_name = forms.CharField(
        label=_('First Name'),
        widget=forms.TextInput(),
        max_length=50
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        widget=forms.TextInput(),
        max_length=50
    )
    password_new = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(render_value=False),
        required=False
    )
    password_new_confirm = forms.CharField(
        label=_("New Password (again)"),
        widget=forms.PasswordInput(render_value=False),
        required=False
    )

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name',
                  'password_new', 'password_new_confirm',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(AccountSettingsForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        value = self.cleaned_data['email'].lower()
        if self.initial.get('email') == value:
            return value
        if MyUser.objects.filter(
                Q(email__iexact=value) & ~Q(pk=self.user.pk)).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return value

    def clean_password_new_confirm(self):
        if not self.cleaned_data['password_new_confirm'] == '':
            clean_passwords(data=self.cleaned_data,
                            password1="password_new",
                            password2="password_new_confirm")
        return self.cleaned_data['password_new_confirm']


class MyUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    def __init__(self, *args, **kargs):
        super(MyUserChangeForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = MyUser
        fields = '__all__'

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        value = self.cleaned_data['email'].lower()
        if self.initial.get('email') == value:
            return value
        if MyUser.objects.filter(email__iexact=value).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return value
