from django.shortcuts import get_object_or_404, redirect, render

from .models import Event

# Create your views here.


def list(request):
    featured_events = Event.objects.featured(num_returned=5)

    context = {
        'featured_events': featured_events,
    }
    return render(request, 'events/list.html', context)


def detail(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    return render(request, 'events/detail.html', {'event': event})
