import random
from typing import List

from django.core.management.base import BaseCommand
from menu.factories.menu_item_factory import MenuItemFactory
from menu.models.menu_item import MenuItem


class Command(BaseCommand):
    help = "Create random menu items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            required=True,
            help="Number random menu items.",
        )
        parser.add_argument(
            "--one-tree", action="store_true", help="Create only one tree."
        )

    def handle(self, *args, **options):
        count = options["count"]
        one_tree = options["one_tree"]

        items: List[MenuItem] = [
            MenuItemFactory.create() for _ in range(count)
        ]
        for i in range(1, count):
            items[i].parent = (
                random.choice(items[:i])
                if one_tree
                else random.choice((random.choice(items[:i]), None))
            )
            items[i].save()

        self.stdout.write("Done!")
