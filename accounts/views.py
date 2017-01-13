from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from billing.models import Customer, Plan
from events.models import Event
from .forms import AccountSettingsForm
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
@never_cache
@sensitive_post_parameters()
def account_settings(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    form = AccountSettingsForm(request.POST or None,
                               request.FILES or None,
                               instance=user, user=user)

    if request.method == 'POST' and form.is_valid():
        form.email = form.cleaned_data['email']
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
        'customer': customer,
        'user': user,
    }
    return render(request, 'accounts/settings.html', context)


def memberships(request):
    plans = Plan.objects.active()
    return render(request, 'auth/memberships.html', {'plans': plans})
