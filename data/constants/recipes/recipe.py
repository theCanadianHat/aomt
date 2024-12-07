from typing import List, Optional

from util.quantity import Quantity


class Item:

    def __init__(self, item_id: str, recipe: Optional['Recipe'] = None):
        self.name = item_id
        self.description = ''
        self.recipe = recipe
        # item ID used with AO Data
        self.item_id = item_id

    def __str__(self):
        if self.recipe and self.recipe.inputs:
            to_string = f"To craft {self.item_id}, you need:\n"
            for i in self.recipe.inputs:
                to_string += f"\t{i.quantity}: {i.content.item_id}\n"
                return to_string
        return f"Item: {self.item_id}, No recipe available"

    def __repr__(self):
        return self.__str__()

class Recipe:

    def __init__(self, inputs: List[Quantity['Item']] = None, output: Quantity['Item'] = None):
        self.inputs = inputs if inputs is not None else []
        self.output = output
