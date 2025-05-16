from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def test_draw_menu(request: HttpRequest, subpath: str) -> HttpResponse:
    target: str = subpath.strip("/").split("/")[-1]
    return render(request, "menu/index.html", context={"target": target})
