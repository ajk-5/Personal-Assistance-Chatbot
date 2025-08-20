from django.db import models

class Reminder(models.Model):
    message = models.CharField(max_length=255)
    due_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)

    class Meta:
        ordering = ["delivered", "due_at", "id"]

    def __str__(self):
        return self.message
