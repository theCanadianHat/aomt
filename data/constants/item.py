from data.constants.recipes.recipe import Recipe


class Item:

    def __init__(self, item_id: str, name: str, description: str, recipe: Recipe):
        self.name = name
        self.description = description
        self.recipe = recipe
        # item ID used with AO Data
        self.item_id = item_id
