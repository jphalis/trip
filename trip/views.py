from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page

# Create views here.


# @cache_page(60 * 5)
def home(request):
    next_url = request.GET.get('next', '/')
    return render(request, 'general/index.html', {'next': next_url})

@login_required
def about(request):
    return render(request, 'general/about.html', {})


def events(request):
    return render(request, 'events/events.html', {})


def sponsors(request):
    return render(request, 'sponsors/sponsors.html', {})
