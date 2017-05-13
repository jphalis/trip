from django.shortcuts import get_object_or_404, render

from .models import Event

# Create your views here.


def list(request):
    ctx = {
        'events': Event.objects.active(),
        'featured_events': Event.objects.featured(num_returned=5),
    }
    return render(request, 'events/list.html', ctx)


def detail(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    attending = event.attendees.filter(
        email__iexact=request.user.email).exists()
    ctx = {
        'event': event,
        'member_attending': attending
    }
    return render(request, 'events/detail.html', ctx)


def reg_success(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    return render(request, 'events/success.html', {'event': event})
