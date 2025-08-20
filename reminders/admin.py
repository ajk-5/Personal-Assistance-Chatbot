from django.contrib import admin
from .models import Reminder

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "due_at", "delivered", "created_at")
    list_filter = ("delivered",)
    search_fields = ("message",)
