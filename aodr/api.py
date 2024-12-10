from typing import List, Union

import requests

from data.constants.recipes.recipe import Recipe, Item
from util.quantity import Quantity

CRAFTRESOURCE = 'craftresource'

CRAFTINGREQUIREMENTS = 'craftingrequirements'

UNIQUENAME = '@uniquename'

DEBUG = False
ITEMS_URL = 'https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/items.json'
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


def __create_item(items: Union[List[dict], dict]) -> Item:
    if isinstance(items, dict):
        unique_name = items[UNIQUENAME]
        if CRAFTINGREQUIREMENTS in items:
            reqs = items[CRAFTINGREQUIREMENTS]
            res: List = reqs[CRAFTRESOURCE]
            if res:
                if DEBUG:
                    print("{} requires resources to craft".format(items[UNIQUENAME]))
                    for r in res:
                        print('\t{}: {}'.format(res[r]['@count'], res[r][UNIQUENAME]))
            return Item(unique_name, __create_recipe(res))

    if isinstance(items, list):
        for item in items:
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
                    return Item(unique_name, __create_recipe(res))


def get_item_data():
    response = requests.get(ITEMS_URL)
    items_json = response.json()
    items = items_json['items']
    for item_type in items:
        if __is_craftable_item(item_type):
            item = items[item_type]
            ITEMS.append(__create_item(item))
    print(ITEMS)
    print('{} items added to list'.format(len(ITEMS)))


if __name__ == '__main__':
    get_item_data()
