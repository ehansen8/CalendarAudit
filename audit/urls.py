from django.urls import path
from . import views

app_name = "audit"
urlpatterns = [
    path("", views.index, name="index"),
    path("watch/", views.watch, name="watch")
]
