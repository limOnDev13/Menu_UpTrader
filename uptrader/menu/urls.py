"""Module with urlpatterns."""

from django.urls import path

from .views import test_draw_menu

app_name = "menu"

urlpatterns = [
    path("test/", test_draw_menu, name="index"),
]
