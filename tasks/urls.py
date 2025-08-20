from django.urls import path
from . import views

app_name = "tasks"
urlpatterns = [
    path("", views.list_tasks, name="list"),
    path("complete/<int:pk>/", views.complete_task, name="complete"),
]
