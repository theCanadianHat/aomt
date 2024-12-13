from enum import Enum, auto
from typing import List, Optional

from util.quantity import Quantity


class ItemType(Enum):
    UNKNOWN = auto()
    RESOURCE = auto()
    ARMOUR = auto()
    WEAPON = auto()
    GATHER = auto()
    TOOL = auto()
    TOKEN = auto()
    ARENA_TOKEN = auto()


class Tier(Enum):
    UNKNOWN = auto()
    ONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()


class ItemRef:
    def __init__(self, item_id: str, item_name: str = None):
        self.item_id = item_id
        self.item_name = item_name


class Item(ItemRef):

    def __init__(self, item_id: str, recipes: Optional['[Recipe]'] = None):
        ItemRef.__init__(self, item_id, item_id)
        self.description = ''
        self.recipes = recipes if recipes is not None else []
        self.item_type = ItemType.UNKNOWN

    def __str__(self):
        return to_json_string(self, indent=2)

    def __repr__(self):
        return self.__str__()

    def print_recipe(self):
        if self.recipe and self.recipe.inputs:
            to_string = f"To craft {self.item_id}, you need:\n"
            for i in self.recipe.inputs:
                to_string += f"\t{i.quantity}: {i.content.item_id}\n"
                return to_string
        return f"Item: {self.item_id}, No recipe available"


class Recipe:

    def __init__(self, inputs: List[Quantity[ItemRef]] = None, output: Quantity[ItemRef] = None):
        self.inputs = inputs if inputs is not None else []
        self.output = output

    def __str__(self):
        return to_json_string(self, indent=2)

    def __repr__(self):
        return self.__str__()


def to_json_string(obj, indent=0, visited=None):
    if visited is None:
        visited = set()

    def format_value(value, indent_level):
        if isinstance(value, (str, int, float, bool, type(None))):
            return f"\"{value}\"" if isinstance(value, str) else str(value)
        elif isinstance(value, list):
            items = [format_value(item, indent_level + 2) for item in value]
            return "[\n" + ",\n".join(
                " " * (indent_level + 2) + item for item in items) + "\n" + " " * indent_level + "]"
        elif isinstance(value, Enum):
            return f"\"{value.name}\""
        elif hasattr(value, '__dict__'):
            return to_json_string(value, indent_level, visited)
        else:
            return str(value)

    if id(obj) in visited:
        return "\"<circular reference>\""

    visited.add(id(obj))
    obj_dict = obj.__dict__
    items = [f"\"{key}\": {format_value(value, indent + 2)}" for key, value in obj_dict.items()]
    visited.remove(id(obj))
    return "{\n" + ",\n".join(" " * (indent + 2) + item for item in items) + "\n" + " " * indent + "}"
