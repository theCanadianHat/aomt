from typing import List, Union

import requests

from data.constants.recipes.recipe import Recipe, Item
from util.quantity import Quantity

CRAFTRESOURCE = 'craftresource'

CRAFTINGREQUIREMENTS = 'craftingrequirements'

UNIQUENAME = '@uniquename'

DEBUG = False
ITEMS_URL = 'https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/items.json'
FORMATTED_ITEMS_URL = 'https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/formatted/items.json'
ITEMS: List[Item] = []

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


def __is_craftable_item(item_type: str) -> bool:
    try:
        return CRAFTABLE_ITEM_TYPES.index(item_type) > 0
    except ValueError:
        return False


def __create_recipe(data: Union[List[dict], dict]) -> Recipe:
    recipe = Recipe([])
    if isinstance(data, list):
        for item in data:
            recipe.inputs.append(Quantity(Item(item['@uniquename']), item['@count']))
    elif isinstance(data, dict):
        recipe.inputs.append(Quantity(Item(data['@uniquename']), data['@count']))
    return recipe


def __create_and_populate_items(items: Union[List[dict], dict]):
    if isinstance(items, dict):
        if UNIQUENAME in items:
            unique_name = items[UNIQUENAME]
            if CRAFTINGREQUIREMENTS in items:
                reqs = items[CRAFTINGREQUIREMENTS]
                res: List = reqs[CRAFTRESOURCE]
                if res:
                    if DEBUG:
                        print("{} requires resources to craft".format(items[UNIQUENAME]))
                        for r in res:
                            print('\t{}: {}'.format(res[r]['@count'], res[r][UNIQUENAME]))
                ITEMS.append(Item(unique_name, __create_recipe(res)))
            else:
                ITEMS.append(Item(unique_name, Recipe()))

    if isinstance(items, list):
        for item in items:
            if UNIQUENAME in item:
                unique_name = item[UNIQUENAME]
                if CRAFTINGREQUIREMENTS in item:
                    reqs = item[CRAFTINGREQUIREMENTS]
                    if CRAFTRESOURCE in reqs:
                        res = reqs[CRAFTRESOURCE]
                        if DEBUG:
                            print("{} requires resources to craft".format(item[UNIQUENAME]))
                        if isinstance(res, list):
                            for r in res:
                                if DEBUG:
                                    print('\t{}: {}'.format(r['@count'], r[UNIQUENAME]))
                        else:
                            if DEBUG:
                                print('\t{}: {}'.format(res['@count'], res[UNIQUENAME]))
                        ITEMS.append(Item(unique_name, __create_recipe(res)))
                else:
                    ITEMS.append(Item(unique_name, Recipe()))


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
                        item_to_update.name = record['LocalizedNames']['EN-US']
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
    return next(filter(lambda i: i.name == item_name, get_item_data()), None)


if __name__ == '__main__':
    get_item_data()
