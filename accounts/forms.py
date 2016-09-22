"""
Glossary of accounts/forms.py:

- Account settings form
- Login form
- MyUser change form (admin only)
- MyUser creation form (admin only)
- Password reset form
- Password reset token form
- Signup form
"""

from __future__ import unicode_literals

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = None

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
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


class MyUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given fields.
    """
    def __init__(self, *args, **kargs):
        super(MyUserCreationForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name',)

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


class LoginForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email'}),
        max_length=120
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password'},
            render_value=False)
    )

    def clean_email(self):
        """
        Makes the value of the email lowercase.
        """
        value = self.cleaned_data.get("email").lower()
        if MyUser.objects.filter(Q(email__iexact=value) &
                                 Q(is_active=False)).exists():
            raise forms.ValidationError("This account has been disabled")
        return value


class SignupForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email'}),
        max_length=120
    )
    first_name = forms.CharField(
        label=_('First name'),
        widget=forms.TextInput(
            attrs={'placeholder': 'First name'},),
        max_length=50
    )
    last_name = forms.CharField(
        label=_('Last name'),
        widget=forms.TextInput(
            attrs={'placeholder': 'Last name'},),
        max_length=50
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password'},
            render_value=False)
    )
    password_confirm = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password confirm'},
            render_value=False)
    )

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        value = self.cleaned_data['email'].lower()
        if MyUser.objects.filter(email__iexact=value):
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return value

    def clean_password_confirm(self):
        clean_passwords(data=self.cleaned_data,
                        password1="password",
                        password2="password_confirm")
        return self.cleaned_data['password_confirm']


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.widgets.EmailInput(
            attrs={'placeholder': 'Email'})
    )

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = subject_template_name
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body,
                                               from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name,
                                                 context)
            email_message.attach_alternative(html_email, 'text/html')
        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = MyUser._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, subject_template_name='KnobLinx Reset Password',
             email_template_name='accounts/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=settings.DEFAULT_HR_EMAIL, request=None,
             html_email_template_name='accounts/password_reset_email.html',
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"].lower()
        for user in self.get_users(email):
            context = {
                'email': user.email,
                'domain': request.get_host(),
                'site_name': request.META['SERVER_NAME'],
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)


class PasswordResetTokenForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password.
    """
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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordResetTokenForm, self).__init__(*args, **kwargs)

    def clean_password_confirm(self):
        clean_passwords(data=self.cleaned_data,
                        password1="password_new",
                        password2="password_new_confirm")

    def save(self, commit=True):
        """
        Saves the form and sets the user's password to be the value he/she
        typed in.
        """
        user = self.user
        if user:
            user.set_password(self.cleaned_data["password_new_confirm"])
            if commit:
                user.save()
            return user
