import random
from typing import Dict, List, Set

from django.test import TestCase
from menu.factories.menu_item_factory import MenuItemFactory
from menu.models.menu_item import MenuItem
from menu.services.menu_funcs import (
    MenuItemSchema,
    get_menu_branch,
    update_parent,
)


class TestGetMenuBranch(TestCase):

    def setUp(self):
        self.n: int = 5000
        self.menu_items: List[MenuItem] = [
            MenuItemFactory.create() for _ in range(self.n)
        ]

        self.names: Set[str] = {item.name for item in self.menu_items}

        for i in range(1, self.n):
            self.menu_items[i].parent = random.choice(
                (self.menu_items[random.randint(0, i - 1)], None)
            )
            if self.menu_items[i].parent is not None:
                self.menu_items[i].url = (
                    f"{self.menu_items[i].parent.url}{self.menu_items[i].name}/"
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
        print(f"{set_children1=} {set_children2=}")
        return result and set_children1 == set_children2

    @classmethod
    def compare_trees(
        cls, tree1: MenuItemSchema, tree2: MenuItemSchema
    ) -> bool:
        print(f"{tree1=} {tree2=}")
        if not cls.compare_nodes(tree1, tree2):
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
    def create_trees(cls, node_name: str) -> List[MenuItemSchema]:
        parents: Set[MenuItem] = set()
        roots: Set[MenuItem] = set()
        target_nodes: List[MenuItem] = (
            MenuItem.objects.select_related("parent")
            .filter(name=node_name)
            .all()
        )

        # соберем предков
        for target in target_nodes:
            cur_node = target
            while cur_node is not None:
                parents.add(cur_node)
                if cur_node.parent is not None:
                    cur_node = MenuItem.objects.select_related("parent").get(
                        id=cur_node.parent.pk
                    )
                else:
                    roots.add(cur_node)
                    cur_node = None

        nodes: Dict[int, MenuItemSchema] = dict()
        for root in roots:
            nodes[root.pk] = MenuItemSchema(
                id=root.pk,
                parent_id=None,
                name=root.name,
                url=root.url,
            )

        def tree(node: MenuItem):
            nonlocal nodes
            nonlocal parents
            children: List[MenuItem] = (
                MenuItem.objects.select_related("parent")
                .filter(parent__id=node.pk)
                .all()
            )
            node_children: List[MenuItemSchema] = [
                MenuItemSchema(
                    id=child.pk,
                    parent_id=child.parent.pk,
                    name=child.name,
                    url=child.url,
                )
                for child in children
            ]
            for child in node_children:
                nodes[child.id] = child
            nodes[node.pk].children.extend(node_children)

            next_nodes: List[MenuItem] = [
                child for child in children if child in parents
            ]
            if len(next_nodes) == 0:
                return
            for node in next_nodes:
                tree(node)

        for root in roots:
            tree(root)

        return [nodes[root.pk] for root in roots]

    def test_get_menu_test(self):
        print(f"Количество имен: {len(self.names)}")
        for counter, name in enumerate(self.names):
            print(f"\n\n{counter=}")
            print(f"{name=}")
            nodes: List[MenuItem] = [
                item for item in self.menu_items if item.name == name
            ]

            # Есть 2 проблема. Если в один узел имеет имя, и какой-то его предок также имеет такое же имя,
            # то для каждого узла будет собрано два дерева с одинаковыми корнями.
            # Но если пробежаться по обоим рекурсивно, то окажется, что у них разная глубина.
            # Сама функция get_menu_branch решает эту проблему в sql запросе. Но в тесте я это не учел.
            # Я потратил 2 дня, чтобы понять, почему тест отваливался.
            # Чтобы решить проблему, нужно выбирать более глубокое дерево из двух деревьев с одинаковыми корнями
            expected_trees: List[MenuItemSchema] = self.create_trees(name)
            received_trees: List[MenuItemSchema] = get_menu_branch(name)

            for expected_tree, received_tree in zip(
                sorted(expected_trees, key=lambda item: item.id),
                sorted(received_trees, key=lambda item: item.id),
            ):
                self.assertTrue(
                    self.compare_trees(expected_tree, received_tree)
                )

    def test_get_branch_from_one_tree_with_same_names(self):
        n = 100
        name = "hello"
        items: List[MenuItem] = [
            MenuItemFactory.create(name=name) for _ in range(n)
        ]

        for i in range(1, n):
            items[i].parent = items[i - 1]
            items[i].url = f"{items[i].parent.url}{items[i].name}/"
            items[i].save()

        expected_tree: List[MenuItemSchema] = self.create_trees(name)
        received_tree: List[MenuItemSchema] = get_menu_branch(name)

        self.assertEqual(len(expected_tree), 1)
        self.assertEqual(len(received_tree), 1)
        self.assertTrue(self.compare_trees(expected_tree[0], received_tree[0]))

    def test_get_branch_with_one_level_with_same_names(self):
        n = 3
        name = "hello"
        items: List[MenuItem] = [
            MenuItemFactory.create(name=name) for _ in range(n)
        ]

        for i in range(1, n):
            items[i].parent = items[0]
            items[i].url = f"{items[i].parent.url}{items[i].name}/"
            items[i].save()

        for counter in range(n):
            print(f"\n\n{counter=}")
            expected_trees: List[MenuItemSchema] = self.create_trees(name)
            received_trees: List[MenuItemSchema] = get_menu_branch(name)

            for expected_tree, received_tree in zip(
                sorted(expected_trees, key=lambda item: item.id),
                sorted(received_trees, key=lambda item: item.id),
            ):
                self.assertTrue(
                    self.compare_trees(expected_tree, received_tree)
                )


class TestUpdateParent(TestCase):
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
            if self.menu_items[i].parent is not None:
                self.menu_items[i].url = (
                    f"{self.menu_items[i].parent.url}{self.menu_items[i].name}/"
                )

            self.menu_items[i].save()

    def tearDown(self):
        for item in self.menu_items:
            item.delete()

    def check_url(self, item_id: int, correct_url: str) -> None:
        self.assertEqual(
            correct_url,
            MenuItem.objects.select_related("parent").get(pk=item_id).url,
        )
        children = (
            MenuItem.objects.select_related("parent")
            .filter(parent__pk=item_id)
            .all()
        )
        if len(children) == 0:
            return

        for child in children:
            self.check_url(child.pk, correct_url + f"{child.name}/")

    def test_update_parent_on_existing(self):
        # перевесим поочередно все узлы на первый узел

        for item in self.menu_items[1:]:
            update_parent(item.pk, self.menu_items[0].pk)
            self.check_url(item.pk, f"{self.menu_items[0].url}{item.name}/")
