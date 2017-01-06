from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Customer

# Create your views here.


@login_required
@require_http_methods(['POST'])
def update_auto_renew(request):
    customer = get_object_or_404(Customer, user=request.user)

    if customer.auto_renew:
        customer.auto_renew = False
    else:
        customer.auto_renew = True

    customer.save(update_fields=['auto_renew'])
    messages.success(request,
                     "You have updated your preferences.")
    return JsonResponse({'auto_renew': customer.auto_renew})
