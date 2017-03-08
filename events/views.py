from django.shortcuts import get_object_or_404, render

from .models import Event

# Create your views here.


def list(request):
    context = {
        'events': Event.objects.active(),
        'featured_events': Event.objects.featured(num_returned=5),
    }
    return render(request, 'events/list.html', context)


def detail(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    context = {
        'event': event,
        'member_attending': event.attendees.filter(pk=request.user.pk).exists()
    }
    return render(request, 'events/detail.html', context)


def reg_success(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    return render(request, 'events/success.html', {'event': event})
