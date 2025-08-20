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
