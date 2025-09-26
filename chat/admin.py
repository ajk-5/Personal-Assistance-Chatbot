from django.contrib import admin, messages
from .models import Message, TrainingPhrase, SmalltalkPair
from .services import Assistant

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

    actions = ("retrain_intents",)

    def retrain_intents(self, request, queryset):
        try:
            # Use the same assistant instance as the chat view if available
            from . import views as chat_views
            if getattr(chat_views, "assistant", None) is None:
                chat_views.assistant = Assistant()
            msg = chat_views.assistant.router.train()
            messages.success(request, f"Intents retrained: {msg}")
        except Exception as e:
            messages.error(request, f"Retrain failed: {e}")
    retrain_intents.short_description = "Retrain intents (TF‑IDF + Logistic Regression)"


@admin.register(SmalltalkPair)
class SmalltalkPairAdmin(admin.ModelAdmin):
    list_display = ("id", "pattern", "is_regex", "is_active", "created_at")
    list_filter = ("is_active", "is_regex")
    search_fields = ("pattern", "answers")
