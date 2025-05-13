
from typing import List, Tuple, Any, Optional, Dict
from dataclasses import dataclass, field

from django.db import connection


@dataclass
class MenuItemSchema:
    id: int
    parent_id: Optional[int]
    name: str
    url: str
    children: List["MenuItemSchema"]= field(default_factory=list)


def get_menu_branch(menu_name: str) -> List[MenuItemSchema]:
    """
    Get subtrees that includes an item with name menu_name.

    The function returns the list of MenuItemSchema,
    the roots of the subtrees, which include all the child elements
    of each parent element, starting with the element with name menu_name.

    :param menu_name: Menu item name.
    :return: List of the roots subtrees.
    """
    query: str = """
    WITH RECURSIVE parents AS (
    SELECT 
        id,
        parent_id,
        0 AS level
    FROM menu_menuitem
    WHERE name = %s
    
    UNION ALL
    
    SELECT
        m.id,
        m.parent_id,
        p.level + 1 AS level
    FROM menu_menuitem m
    JOIN parents p ON m.id = p.parent_id
    )
    
    SELECT
        menu.id, 
        menu.parent_id, 
        menu.name, 
        menu.url,
        pt.level AS level
    FROM menu_menuitem menu
    INNER JOIN parents pt ON menu.parent_id = pt.id
    UNION
    SELECT
        menu.id,
        menu.parent_id,
        menu.name,
        menu.url,
        pt.level + 1 AS level
    FROM menu_menuitem menu
    INNER JOIN parents pt ON menu.id = pt.id
    ORDER BY level DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (menu_name,))
        nodes: Dict[int, MenuItemSchema] = dict()
        roots: List[MenuItemSchema] = list()

        for item in cursor.fetchall():
            print(item)
            menu_item = MenuItemSchema(
                id=item[0],
                parent_id=item[1],
                name=item[2],
                url=item[3]
            )
            nodes[menu_item.id] = menu_item

            if menu_item.parent_id is not None:
                # мы не должны получить IndexError, так как в sql запросе отсортировали узлы по глубине
                nodes[menu_item.parent_id].children.append(menu_item)
            else:
                # если нет родителя - это корневой узел
                roots.append(nodes[item[0]])

        return roots
