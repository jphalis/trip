from django.shortcuts import render

from .models import Event

# Create your views here.


def event_list(request):
    return render(request, 'events/list.html', {})


def event_detail(request, event_pk):
    return render(request, 'events/detail.html', {})
