from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .models import Membership

# Create your views here.


@login_required
@require_http_methods(['POST'])
def update_auto_renew(request):
    membership = get_object_or_404(Membership, user=request.user)

    if membership.auto_renew:
        membership.auto_renew = False
    else:
        membership.auto_renew = True

    membership.save(update_fields=['auto_renew'])
    messages.success(request,
                     "You have updated your preferences.")
    return JsonResponse({'auto_renew': membership.auto_renew})
