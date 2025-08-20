from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "due_at"]

@require_http_methods(["GET", "POST"])
def list_tasks(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tasks:list")
    else:
        form = TaskForm()
    tasks = Task.objects.all()
    return render(request, "tasks/list.html", {"tasks": tasks, "form": form})

@require_http_methods(["POST"])
def complete_task(request, pk: int):
    t = get_object_or_404(Task, pk=pk)
    t.is_completed = True
    t.save(update_fields=["is_completed"])
    return redirect("tasks:list")
