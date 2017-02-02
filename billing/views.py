from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Customer, Subscription
from .utils import get_or_create_stripe_sub, cancel_stripe_sub

# Create your views here.


@login_required
@require_http_methods(['POST'])
def update_auto_renew(request):
    customer = get_object_or_404(Customer, user=request.user)
    customer.auto_renew = False if customer.auto_renew else True
    customer.save(update_fields=['auto_renew'])

    sub = Subscription.objects.filter(customer=customer).order_by('created')[0]

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

        messages.success(request,
                         "You have updated your preferences.")
        return JsonResponse({'auto_renew': customer.auto_renew})
    else:
        messages.error(request,
                       "There was an error with your request.")
    return JsonResponse('Error.')
