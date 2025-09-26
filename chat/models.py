from django.db import models

class Message(models.Model):
    SENDER_CHOICES = [("user", "User"), ("assistant", "Assistant")]
    sender = models.CharField(max_length=16, choices=SENDER_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class TrainingPhrase(models.Model):
    label = models.CharField(max_length=64)  # e.g. tasks, notes, reminders, events, time, smalltalk
    text = models.CharField(max_length=255)

    class Meta:
        unique_together = ("label", "text")
        indexes = [models.Index(fields=["label"])]


class SmalltalkPair(models.Model):
    """Admin-trainable smalltalk patterns and reply options.

    - pattern: literal substring or regex to match user input
    - is_regex: treat pattern as regex if true
    - answers: newline- or pipe-separated possible replies; one is chosen at random
    """
    pattern = models.CharField(max_length=200)
    is_regex = models.BooleanField(default=False)
    answers = models.TextField(help_text="Enter multiple replies separated by newlines or | characters.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self) -> str:
        return self.pattern
