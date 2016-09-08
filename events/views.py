from django.shortcuts import render

from .models import Event

# Create your views here.


def list(request):
    return render(request, 'events/list.html', {})


def detail(request, event_pk):
    return render(request, 'events/detail.html', {})
