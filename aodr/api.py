from typing import List, Union, Optional

import requests

from data.constants.recipes.recipe import Recipe, Item, ItemRef, to_json_string
from util.quantity import Quantity

CRAFTRESOURCE = 'craftresource'

CRAFTINGREQUIREMENTS = 'craftingrequirements'

UNIQUENAME = '@uniquename'

DEBUG = False
ITEMS_URL = 'https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/items.json'
FORMATTED_ITEMS_URL = 'https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/formatted/items.json'
ITEMS: List[Item] = []


class RawDataKeys:
    UNIQUE_NAME = '@uniquename'
    SHOP_CATEGORY = '@shopcategory'
    SHOP_SUBCATEGORY1 = '@shopsubcategory1'
    CRAFTING_CATEGORY = '@craftingcategory'
    TIER = '@tier'
    WEIGHT = '@weight'
    MAX_STACK_SIZE = '@maxstacksize'
    UI_CRAFT_SOUND_START = '@uicraftsoundstart'
    UI_CRAFT_SOUND_FINISH = '@uicraftsoundfinish'
    FAST_TRAVEL_FACTOR = '@fasttravelfactor'
    ITEM_VALUE = '@itemvalue'
    ENCHANTMENT_LEVEL = '@enchantmentlevel'
    DESCRIPTION_LOCATAG = '@descriptionlocatag'
    CRAFTING_REQUIREMENTS = 'craftingrequirements'
    SILVER = '@silver'
    TIME = '@time'
    CRAFTING_FOCUS = '@craftingfocus'
    AMOUNT_CRAFTED = '@amountcrafted'
    CRAFT_RESOURCE = 'craftresource'
    COUNT = '@count'


'''
items.@xmlns:xsi
items.@xsi:noNamespaceSchemaLocation
items.shopcategories
items.hideoutitem
items.trackingitem
items.farmableitem
items.simpleitem
items.consumableitem
items.consumablefrominventoryitem
items.trashitem
items.equipmentitem
items.weapon
items.mount
items.furnitureitem
items.mountskin
items.journalitem
items.labourercontract
items.transformationweapon
items.crystalleagueitem
items.siegebanner
items.killtrophy

--- crafting requirements
hideoutitem
trackingitem
farmableitem
simpleitem
consumableitem
consumablefrominventoryitem
trashitem
equipmentitem
weapon
mount
furnitureitem
mountskin
journalitem
labourercontract
transformationweapon
crystalleagueitem
siegebanner

--- example structure

{
    '@uniquename':str,
    'craftingrequirements' : {
        'craftresource' : [
            {
                '@uniquename': 'T2_PLANKS,
                '@count': '4'
            },
            {
                '@uniquename': 'T2_METALBAR',
                '@count': '4'
            }
        ]
    }
}

'''

CRAFTABLE_ITEM_TYPES = [
    'hideoutitem',
    'trackingitem',
    'farmableitem',
    'simpleitem',
    'consumableitem',
    'consumablefrominventoryitem',
    'trashitem',
    'equipmentitem',
    'weapon',
    'mount',
    'furnitureitem',
    'mountskin',
    'journalitem',
    'labourercontract',
    'transformationweapon',
    'crystalleagueitem',
    'siegebanner'
]


# external
class CraftResource:
    def __init__(self,
                 unique_name: str,
                 count: int,
                 enchantment_level: int = 0):
        self.unique_name = unique_name
        self.count = count
        self.enchantment_level = enchantment_level

    @classmethod
    def from_dict(cls, data: Union[dict, list]):
        if isinstance(data, list):
            return [cls.from_dict(d) for  d in data]
        return cls(
            unique_name=data.get(RawDataKeys.UNIQUE_NAME, ''),
            count=int(data.get(RawDataKeys.COUNT, 0)),
            enchantment_level=int(data.get(RawDataKeys.ENCHANTMENT_LEVEL, 0))
        )

    def __str__(self):
        return to_json_string(self, indent=2)

    def __repr__(self):
        return self.__str__()


class CraftingRequirement:
    def __init__(self,
                 silver: int = 0,
                 amount_crafted: int = 0,
                 craft_resource: Optional[List[CraftResource]] = None):
        self.silver = silver
        self.amount_crafted = amount_crafted
        self.craft_resources = craft_resource if craft_resource is not None else []

    @classmethod
    def from_dict(cls, data: Union[dict, list]):
        if isinstance(data, list):
            return [cls.from_dict(d) for  d in data]
        craft_resource = CraftResource.from_dict(data.get(CRAFTRESOURCE, []))
        return cls(
            silver=int(data.get(RawDataKeys.SILVER, 0)),
            amount_crafted=int(data.get(RawDataKeys.AMOUNT_CRAFTED, 1)),
            craft_resource=craft_resource
        )

    def __str__(self):
        return to_json_string(self, indent=2)

    def __repr__(self):
        return self.__str__()


class ExternalItem:
    def __init__(self,
                 unique_name: str = '',
                 tier: int = 0,
                 enchantment_level: int = 0,
                 crafting_requirements: Optional[List[CraftingRequirement]] = None):
        self.unique_name = unique_name
        self.tier = tier
        self.enchantment_level = enchantment_level
        self.crafting_requirements = crafting_requirements if crafting_requirements is not None else []

    @classmethod
    def from_dict(cls, data: dict):
        crafting_requirements = CraftingRequirement.from_dict(data.get(RawDataKeys.CRAFTING_REQUIREMENTS, []))
        return cls(
            unique_name=data.get(RawDataKeys.UNIQUE_NAME, ''),
            tier=int(data.get(RawDataKeys.TIER, 0)),
            enchantment_level=int(data.get(RawDataKeys.ENCHANTMENT_LEVEL, 0)),
            crafting_requirements=crafting_requirements
        )

    def __str__(self):
        return to_json_string(self, indent=2)

    def __repr__(self):
        return self.__str__()


RAW_ITEMS: List[ExternalItem] = []


def get_raw_items():
    return RAW_ITEMS


def __is_craftable_item(item_type: str) -> bool:
    try:
        return CRAFTABLE_ITEM_TYPES.index(item_type) > 0
    except ValueError:
        return False


def __create_recipe(data: Union[List[dict], dict]) -> Recipe:
    recipe = Recipe([])
    if isinstance(data, list):
        for item in data:
            recipe.inputs.append(Quantity(ItemRef(item['@uniquename']), item['@count']))
    elif isinstance(data, dict):
        recipe.inputs.append(Quantity(ItemRef(data['@uniquename']), data['@count']))
    return recipe


def __create_recipe_list(crafting_requirements):
    recipes: [Recipe] = []
    # has single Recipe
    if isinstance(crafting_requirements, dict):
        # can use resources to craft
        if CRAFTRESOURCE in crafting_requirements:
            crafting_resource = crafting_requirements[CRAFTRESOURCE]
            if crafting_resource:
                recipes.append(__create_recipe(crafting_resource))
    # has multiple recipes
    if isinstance(crafting_requirements, list):
        for index, requirement in enumerate(crafting_requirements):
            if CRAFTRESOURCE in requirement:
                crafting_res = requirement[CRAFTRESOURCE]
                if crafting_res:
                    recipes.append(__create_recipe(crafting_res))
    return recipes


def __create_and_add_item(item):
    unique_name = item[UNIQUENAME]
    # has a recipe
    if CRAFTINGREQUIREMENTS in item:
        crafting_requirements = item[CRAFTINGREQUIREMENTS]
        recipes: [Recipe] = __create_recipe_list(crafting_requirements)
        ITEMS.append(Item(unique_name, recipes))
    else:
        ITEMS.append(Item(unique_name, Recipe()))


def __create_and_populate_items(items: Union[List[dict], dict]):
    # single Item
    if isinstance(items, dict):
        if UNIQUENAME in items:
            __create_and_add_item(items)
            RAW_ITEMS.append(ExternalItem.from_dict(items))

    if isinstance(items, list):
        for item in items:
            if UNIQUENAME in item:
                __create_and_add_item(item)
                RAW_ITEMS.append(ExternalItem.from_dict(item))


def get_item_data() -> List[Item]:
    if len(ITEMS):
        if DEBUG:
            print(ITEMS)
        return ITEMS
    else:
        response = requests.get(ITEMS_URL)
        items_json = response.json()
        items = items_json['items']
        for item_type in items:
            item_list = items[item_type]
            if not isinstance(item_list, str):
                __create_and_populate_items(item_list)

        # populate items with names and descriptions (formatted items.json)
        formatted_response = requests.get(FORMATTED_ITEMS_URL)
        formatted_items_json = formatted_response.json()
        unique_item_names = [i.item_id for i in ITEMS]
        for record in formatted_items_json:
            map_it = False
            record_un = record['UniqueName']
            try:
                map_it = unique_item_names.index(record_un) > 0
            except ValueError:
                map_it = False
            if map_it:
                item_to_update: Item = next(filter(lambda i: i.item_id == record_un, ITEMS), None)

                if item_to_update:
                    try:
                        item_to_update.item_name = record['LocalizedNames']['EN-US']
                        item_to_update.description = record['LocalizedDescriptions']['EN-US']
                    except TypeError:
                        if DEBUG:
                            print(f"{record_un} doesn't have name or description")

        if DEBUG:
            print(ITEMS)
        return ITEMS


def get_item_by_id(item_id: str) -> Item | None:
    return next(filter(lambda i: i.item_id == item_id, get_item_data()), None)


def get_item_by_name(item_name: str) -> Item | None:
    return next(filter(lambda i: i.item_name == item_name, get_item_data()), None)


if __name__ == '__main__':
    get_item_data()
