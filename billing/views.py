from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from contact.models import Newsletter
from events.models import Attendee, Event
from .forms import StripeCreditCardForm
from .models import Customer, Subscription
from .utils import get_or_create_stripe_sub, cancel_stripe_sub

# Create your views here.


@login_required
@require_http_methods(['POST'])
def update_auto_renew(request):
    customer = get_object_or_404(Customer, user=request.user)
    customer.auto_renew = False if customer.auto_renew else True
    customer.save(update_fields=['auto_renew'])
    sub = Subscription.objects.filter(
        customer=customer).order_by('created').first()

    if sub:
        if sub.cancel_at_period_end:
            stripe_sub = get_or_create_stripe_sub(subscription_id=sub.sub_id,
                                                  customer=customer.cu_id,
                                                  plan=sub.plan.plan_id)
        else:
            stripe_sub = cancel_stripe_sub(subscription_id=sub.sub_id,
                                           at_period_end=True)

        sub.cancel_at_period_end = stripe_sub['cancel_at_period_end']
        sub.save(update_fields=['cancel_at_period_end'])

        messages.success(request, _("You have updated your preferences."))
        return JsonResponse({'auto_renew': customer.auto_renew})

    messages.error(request, _("There was an error with your request."))
    return JsonResponse(_('Error.'))


def _add_to_event(event, email, first_name, last_name):
    """
    Adds a user to the event, and adds them to the newsletter.
    """
    attendee = Attendee.objects.create(email=email, first_name=first_name,
                                       last_name=last_name)
    event.attendees.add(attendee)
    Newsletter.objects.get_or_create(email=email, first_name=first_name,
                                     last_name=last_name)
    return True


def checkout(request, event_pk):
    user = request.user
    event = get_object_or_404(Event, pk=event_pk)
    is_auth = user.is_authenticated()
    is_attending = event.attendees.filter(email__iexact=user.email).exists()
    event_price = event.member_fee if is_auth else event.non_member_fee

    # Forbid if user is already attending
    if is_auth and is_attending:
        return HttpResponseForbidden()

    # User is authenticated and not registered for the event
    if is_auth and event_price == 0 and not is_attending:
        _add_to_event(event=event, email=user.email,
                      first_name=user.first_name, last_name=user.last_name)
        return redirect(event.get_reg_success_url())

    try:
        cu = Customer.objects.get(user=user if is_auth else None)
    except Customer.DoesNotExist:
        cu = None

    form = StripeCreditCardForm(request.POST or None,
                                user=user if is_auth else None,
                                customer=cu)

    # Create the charge
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']

        # User is not authenticated and not registered for the event
        if not event.attendees.filter(email__iexact=email).exists():
            charge = form.charge_customer(
                amount=event_price,
                description='Charge from {} for {}'.format(email, event.name),
                receipt_email=email
            )

            # Charge was created
            if charge:
                _add_to_event(event=event, email=email,
                              first_name=form.cleaned_data['first_name'],
                              last_name=form.cleaned_data['last_name'])
                return redirect(event.get_reg_success_url())

            # Error creating charge
            messages.error(request,
                           _('There was an error processing your request.'))
        # User already registered for event
        messages.error(request,
                       _('This email is already registered for this event.'))

    context = {'form': form, 'event_price': event_price}
    return render(request, 'billing/checkout.html', context)
