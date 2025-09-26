from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("", views.chat, name="chat"),
    path("retrain/", views.retrain, name="retrain"),
    path("status/", views.status, name="status"),
]
