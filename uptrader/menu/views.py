from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def test_draw_menu(request: HttpRequest) -> HttpResponse:
    return render(request, "menu/index.html", context={"target": "target"})
