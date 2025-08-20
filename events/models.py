from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["starts_at", "id"]

    def __str__(self) -> str:
        return self.title
