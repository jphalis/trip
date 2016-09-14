from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page

from accounts.models import MyUser
from events.models import Event

# Create views here.


# @cache_page(60 * 5)
def home(request):
    next_url = request.GET.get('next', '/')
    featured_events = Event.objects.featured(num_returned=5)

    context = {
        'featured_events': featured_events,
        'next': next_url,
    }
    return render(request, 'general/index.html', context)


def memberships(request):
    return render(request, 'general/memberships.html', {})


def sponsors(request):
    sponsors = MyUser.objects.all().values('name', 'website')
    return render(request, 'sponsors/sponsors.html', {'sponsors': sponsors})
