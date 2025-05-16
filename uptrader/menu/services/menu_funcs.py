from typing import Dict, List, Optional

from django.db import connection, transaction


class MenuItemSchema:
    def __init__(
        self, *, id: int, parent_id: Optional[int], name: str, url: str
    ):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.url = url
        self.children: List["MenuItemSchema"] = list()

    def __repr__(self) -> str:
        return f"(id={self.id} parent_id={self.id} name={self.name} url={self.url} children={self.children})"


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
            name,
            url
        FROM menu_menuitem
        WHERE name = %s
        
        UNION
        
        SELECT
            m.id,
            m.parent_id,
            m.name,
            m.url
        FROM menu_menuitem m
        JOIN parents p ON m.id = p.parent_id
    ),
    children AS (
        SELECT
            m.id,
            m.parent_id,
            m.name,
            m.url
        FROM menu_menuitem m
        JOIN parents p ON m.parent_id = p.id
    )
    
    SELECT * FROM parents
    UNION
    SELECT * FROM children;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (menu_name,))
        nodes: Dict[int, MenuItemSchema] = dict()
        roots: List[MenuItemSchema] = list()

        for item in cursor.fetchall():
            menu_item = MenuItemSchema(
                id=item[0],
                parent_id=item[1],
                name=item[2],
                url=item[3],
            )

            nodes[menu_item.id] = menu_item

        for item in nodes.values():
            if item.parent_id is not None:
                nodes[item.parent_id].children.append(item)
            else:
                roots.append(nodes[item.id])

        return roots


def update_parent(
    menu_item_id: int, new_parent_id: Optional[int] = None
) -> None:
    query: str = """
    WITH RECURSIVE
    new_parent AS (
        SELECT * FROM menu_menuitem WHERE id = %s
    ),
    children AS (
        SELECT 
            m.id,
            m.parent_id,
            m.name,
            m.url,
            np.id AS new_parent_id,
            CONCAT(COALESCE(np.url, ''), m.name, '/') AS new_url
        FROM menu_menuitem m
        CROSS JOIN new_parent AS np
        WHERE m.id = %s
    
        UNION ALL
    
        SELECT
            m.id,
            m.parent_id,
            m.name,
            m.url,
            m.parent_id AS new_parent_id,
            CONCAT(c.new_url, m.name, '/') AS new_url
        FROM menu_menuitem m
        JOIN children c ON m.parent_id = c.id
    )

    UPDATE menu_menuitem AS menu
    SET
        url = ch.new_url,
        parent_id = ch.new_parent_id
    FROM (SELECT * FROM children FOR UPDATE) AS ch
    WHERE menu.id = ch.id;
    """
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(query, (new_parent_id, menu_item_id))
