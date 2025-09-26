from django.urls import path
from . import views

app_name = "reminders"
urlpatterns = [
    path("", views.list_reminders, name="list"),
    path("cancel/<int:pk>/", views.cancel_reminder, name="cancel"),
    path("api/due/", views.api_due, name="api_due"),
]
