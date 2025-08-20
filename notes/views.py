from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "content"]

@require_http_methods(["GET", "POST"])
def list_notes(request):
    q = request.GET.get("q", "")
    qs = Note.objects.all()
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(content__icontains=q)
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("notes:list")
    else:
        form = NoteForm()
    return render(request, "notes/list.html", {"notes": qs, "form": form, "q": q})
