"""The module responsible for menu item factory."""

import factory.fuzzy
from menu.models.menu_item import MenuItem


class MenuItemFactory(factory.django.DjangoModelFactory):
    """
    Menu item factory class.

    To create an instance,
    you must transfer the parent instance.
    For example
    MenuItemFactory.create(parent=parent_instance)
    """

    class Meta:
        model = MenuItem

    name = factory.faker.Faker("word")
    url = factory.faker.Faker("word")
