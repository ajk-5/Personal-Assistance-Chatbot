from django.contrib import admin
from .models import Profile, Project, QAPair, Persona


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "location", "website", "updated_at")
    search_fields = ("display_name", "short_bio", "full_bio", "location")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_active", "order", "url")
    list_filter = ("is_active",)
    search_fields = ("title", "summary", "tags")


@admin.register(QAPair)
class QAPairAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "created_at")
    search_fields = ("question", "answer")


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ("id", "tone", "refer_to_user_as", "third_person")

