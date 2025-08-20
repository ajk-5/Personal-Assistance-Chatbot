from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "starts_at", "location")
    list_filter = ("starts_at",)
    search_fields = ("title", "location")
