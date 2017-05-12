from django.shortcuts import render
from django.views.decorators.cache import cache_page

from accounts.models import Sponsor
from events.models import Event

# Create views here.


@cache_page(60 * 3)
def home(request):
    ctx = {
        'featured_events': Event.objects.featured(num_returned=5),
        'next': request.GET.get('next', '/'),
    }
    return render(request, 'general/index.html', ctx)


def sponsors(request):
    ctx = {
        'sponsors': Sponsor.objects.active()
    }
    return render(request, 'sponsors/sponsors.html', ctx)
