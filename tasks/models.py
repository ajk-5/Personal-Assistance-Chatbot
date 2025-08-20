from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["is_completed", "due_at", "id"]

    def __str__(self) -> str:
        return self.title
