import locale

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.debug import sensitive_post_parameters

from events.models import Event

from .forms import (AccountSettingsForm, LoginForm, PasswordResetForm,
                    PasswordResetTokenForm, SignupForm)
from .models import MyUser

# Create your views here.


@login_required
def detail(request, user_pk):
    user = get_object_or_404(MyUser, pk=user_pk)
    own_events = Event.objects.own(user=user)
    context = {
        'own_events': own_events,
        'user': user,
    }
    return render(request, 'accounts/detail.html', context)


@login_required
def account_settings(request):
    user = request.user
    form = AccountSettingsForm(request.POST or None,
                               request.FILES or None,
                               instance=user, user=user)
    if request.method == 'POST' and form.is_valid():
        form.email = form.cleaned_data['email']
        form.name = form.cleaned_data['name']
        password = form.cleaned_data['password_new_confirm']
        if password:
            current_user = form.user
            current_user.set_password(password)
            current_user.save()
            update_session_auth_hash(request, current_user)
        form.save()
        messages.success(request,
                         "You have successfully updated your profile.")
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'accounts/settings.html', context)


def password_reset(request, from_email=settings.DEFAULT_FROM_EMAIL,
                   template_name='auth/password_reset_form.html',
                   email_template_name='auth/password_reset_email.html',
                   subject_template_name='Trip Reset Account Password',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   html_email_template_name='auth/password_reset_email.html'):
    if request.user.is_authenticated():
        return redirect('home')
    else:
        if request.method == "POST":
            form = password_reset_form(request.POST)
            if form.is_valid():
                opts = {
                    'use_https': request.is_secure(),
                    'token_generator': token_generator,
                    'from_email': from_email,
                    'email_template_name': email_template_name,
                    'subject_template_name': subject_template_name,
                    'request': request,
                    'html_email_template_name': html_email_template_name,
                }
                form.save(**opts)

                messages.success(
                    request,
                    "If that email is registered to an account, "
                    "instructions for resetting your password "
                    "will be sent soon. Please make sure to check "
                    "your junk email/spam folder if you do not "
                    "receive an email.")
        else:
            form = password_reset_form()
        return render(request, template_name, {'form': form})


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           token_generator=default_token_generator):
    assert uidb64 is not None and token is not None
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        form = PasswordResetTokenForm(request.POST or None, user=user)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                login(request, user)
                messages.success(request, "Password reset successfully.")
                return redirect('home')
    else:
        validlink = False
        form = None
        messages.error(request, "Password reset unsuccessful.")
    context = {
        'form': form,
        'validlink': validlink,
    }
    return render(request, 'auth/password_set.html', context)


def auth_logout(request):
    logout(request)
    return redirect('home')


@never_cache
def auth_base_view(request):
    if request.user.is_authenticated():
        return redirect('home')
    next_url = request.GET.get('next', '/')
    return render(request, 'auth/login.html', {'next': next_url})


@never_cache
def auth_login(request):
    next_url = request.GET.get('next', '/')
    login_form = LoginForm(request.POST or None)
    if login_form.is_valid() and 'login_form' in request.POST:
        email = login_form.cleaned_data['email']
        password = login_form.cleaned_data['password']
        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.POST.get('next', 'home'))
        else:
            messages.warning(request, 'Username or password is incorrect.')
            return redirect('accounts:auth_base_view')
    context = {
        'login_form': login_form,
        'next': next_url,
    }
    return render(request, 'auth/_login_form.html', context)


@never_cache
def auth_register(request):
    cost = request.POST['membership_cost']
    register_form = SignupForm(request.POST or None)

    if cost == 'free':
        membership_cost = 'FREE'
    else:
        locale.setlocale(locale.LC_ALL, '')
        membership_cost = locale.currency(float(cost), grouping=True)

    if register_form.is_valid() and 'register_form' in request.POST:
        email = register_form.cleaned_data['email']
        password = register_form.cleaned_data['password_confirm']
        new_user = MyUser.objects.create_user(
            email=email,
            name=register_form.cleaned_data['company_name']
        )
        new_user.set_password(password)
        new_user.save()
        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
    context = {
        'register_form': register_form,
        'membership_cost': membership_cost,
    }
    return render(request, 'auth/register.html', context)
