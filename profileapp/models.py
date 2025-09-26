from django.db import models


class Profile(models.Model):
    display_name = models.CharField(max_length=120)
    short_bio = models.CharField(max_length=300, blank=True)
    full_bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    timezone = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.display_name


class Project(models.Model):
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    tags = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title


class QAPair(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self) -> str:
        return self.question


class Persona(models.Model):
    tone = models.CharField(max_length=50, blank=True, help_text="e.g., friendly, professional, concise")
    greeting_template = models.CharField(max_length=200, blank=True, help_text="e.g., 'Hi, I’m {name}\u2014how can I help?' ")
    closing_template = models.CharField(max_length=200, blank=True, help_text="e.g., 'Happy to help! 44B'")
    refer_to_user_as = models.CharField(max_length=50, blank=True, help_text="How to refer to you, e.g., 'Alex' or 'my creator'")
    third_person = models.BooleanField(default=False, help_text="If true, refer to you in third person.")

    def __str__(self) -> str:
        return f"Persona: {self.tone or 'default'}"

