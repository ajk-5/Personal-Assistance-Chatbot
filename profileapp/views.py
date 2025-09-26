from django.shortcuts import render
from django.views.decorators.http import require_GET
from .models import Profile, Project, QAPair


@require_GET
def about(request):
    profile = Profile.objects.first()
    projects = Project.objects.filter(is_active=True)
    faqs = QAPair.objects.all()[:10]
    return render(request, "profileapp/about.html", {"profile": profile, "projects": projects, "faqs": faqs})

