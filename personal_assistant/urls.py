from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("chat.urls")),
    path("tasks/", include("tasks.urls")),
    path("notes/", include("notes.urls")),
    path("reminders/", include("reminders.urls")),
    path("events/", include("events.urls")),
    path("about/", include("profileapp.urls")),
]
