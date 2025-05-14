import random
from typing import List, Optional, Set

from django.test import TestCase
from menu.factories.menu_item_factory import MenuItemFactory
from menu.models.menu_item import MenuItem
from menu.services.menu_funcs import MenuItemSchema, get_menu_branch


class TestGetMenuBranch(TestCase):

    def setUp(self):
        self.n: int = 1000
        self.menu_items: List[MenuItem] = [
            MenuItemFactory.create() for _ in range(self.n)
        ]

        self.names: Set[str] = {item.name for item in self.menu_items}

        for i in range(1, self.n):
            self.menu_items[i].parent = random.choice(
                (self.menu_items[random.randint(0, i - 1)], None)
            )
            self.menu_items[i].save()

    def tearDown(self):
        for item in self.menu_items:
            item.delete()

    @classmethod
    def compare_nodes(
        cls, node1: MenuItemSchema, node2: MenuItemSchema
    ) -> bool:
        result: bool = node1.id == node2.id
        set_children1: Set[int] = {child.id for child in node1.children}
        set_children2: Set[int] = {child.id for child in node2.children}
        return result and set_children1 == set_children2

    @classmethod
    def compare_trees(
        cls, tree1: MenuItemSchema, tree2: MenuItemSchema
    ) -> bool:
        if not cls.compare_nodes(tree1, tree2):
            print(f"{tree1.name=} {tree2.name=}")
            return False

        for child1 in tree1.children:
            child2 = None
            for child in tree2.children:
                if child.id == child1.id:
                    child2 = child
                    break
            if child2 is None:
                raise ValueError("Why child2 is None if tree1 == tree2?")

            if not cls.compare_trees(child1, child2):
                return False
        return True

    @classmethod
    def create_tree(cls, init_node: MenuItem):
        parents: List[MenuItemSchema] = list()
        cur_node: Optional[MenuItem] = init_node

        # соберем родителей
        while cur_node is not None:
            parents.append(
                MenuItemSchema(
                    id=cur_node.pk,
                    parent_id=(
                        cur_node.parent.pk
                        if cur_node.parent is not None
                        else None
                    ),
                    name=cur_node.name,
                    url=cur_node.url,
                )
            )
            cur_node = cur_node.parent

        # свяжем родителей
        for i in range(len(parents) - 1):
            parents[i + 1].children.append(parents[i])

        # соберем детей для начального узла
        parents[0].children.extend(
            [
                MenuItemSchema(
                    id=child.pk,
                    parent_id=parents[0].id,
                    name=child.name,
                    url=child.url,
                )
                for child in MenuItem.objects.filter(
                    parent__pk=parents[0].id
                ).all()
            ]
        )
        # соберем детей для всех остальных предков
        for parent in parents[1:]:
            parent.children.extend(
                [
                    MenuItemSchema(
                        id=child.pk,
                        parent_id=parent.id,
                        name=child.name,
                        url=child.url,
                    )
                    for child in MenuItem.objects.filter(
                        parent__pk=parent.id
                    ).all()
                    if child.pk != parent.children[0].id
                ]
            )
        return parents[-1]

    def test_get_menu_test(self):
        for name in self.names:
            print(f"\n\n{name=}")
            nodes: List[MenuItem] = [
                item for item in self.menu_items if item.name == name
            ]
            expected_trees: List[MenuItemSchema] = [
                self.create_tree(node) for node in nodes
            ]
            received_trees: List[MenuItemSchema] = get_menu_branch(name)

            for expected_tree, received_tree in zip(
                sorted(expected_trees, key=lambda item: item.id),
                sorted(received_trees, key=lambda item: item.id),
            ):
                self.assertTrue(
                    self.compare_trees(expected_tree, received_tree)
                )
