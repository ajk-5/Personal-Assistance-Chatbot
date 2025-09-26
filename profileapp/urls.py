from django.urls import path
from . import views

app_name = "profileapp"
urlpatterns = [
    path("", views.about, name="about"),
]

