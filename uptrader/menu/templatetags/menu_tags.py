from typing import List

from django import template

from menu.services.menu_funcs import get_menu_branch, MenuItemSchema

register = template.Library()

@register.inclusion_tag('menu/draw_menu.html', takes_context=True)
def draw_menu(context, menu_name):
    menu_items: List[MenuItemSchema] = get_menu_branch(menu_name)
    return {
        'menu_items': menu_items,
        'request': context['request'],
    }
