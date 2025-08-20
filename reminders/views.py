from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django import forms
from .models import Reminder

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ["message", "due_at"]

@require_http_methods(["GET", "POST"])
def list_reminders(request):
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("reminders:list")
    else:
        form = ReminderForm()
    rems = Reminder.objects.all()
    return render(request, "reminders/list.html", {"reminders": rems, "form": form})

@require_http_methods(["POST"])
def cancel_reminder(request, pk: int):
    r = get_object_or_404(Reminder, pk=pk)
    r.delete()
    return redirect("reminders:list")
