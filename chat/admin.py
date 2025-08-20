from django.contrib import admin
from .models import Message, TrainingPhrase

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "text", "created_at")
    list_filter = ("sender",)
    search_fields = ("text",)

@admin.register(TrainingPhrase)
class TrainingPhraseAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "text")
    list_filter = ("label",)
    search_fields = ("text",)
