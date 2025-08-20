from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "starts_at", "ends_at", "location", "details"]

@require_http_methods(["GET", "POST"])
def list_events(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("events:list")
    else:
        form = EventForm()
    events = Event.objects.all()
    return render(request, "events/list.html", {"events": events, "form": form})
