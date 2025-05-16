from typing import List

from django import template
from django.conf import settings
from menu.services.menu_funcs import MenuItemSchema, get_menu_branch

register = template.Library()


@register.inclusion_tag("menu/all_menu.html", takes_context=True)
def draw_menu(context, menu_name):
    menu_items: List[MenuItemSchema] = get_menu_branch(menu_name)
    return {
        "menu_items": [
            [item] for item in menu_items
        ],  # костыль для рекурсивного фронтенда
        "target": menu_name,
        "menu_url": settings.MENU_URL,
        "request": context["request"],
    }
