import requests

ITEMS_URL = 'https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/items.json'

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


def get_item_data():
    response = requests.get(ITEMS_URL)
    items_json = response.json()
    items = items_json['items']
    item_count = 0
    for item_type in items:
        if __is_craftable_item(item_type):
            item = items[item_type]
            if isinstance(item, dict):
                for key in item:
                    if key == 'craftingrequirements':
                        reqs = item[key]
                        res = reqs['craftresource']
                        if res:
                            item_count += 1
                            print("{} requires resources to craft".format(item['@uniquename']))
                            for r in res:
                                print('\t{}: {}'.format(res[r]['@count'], res[r]['@uniquename']))
                        # print(item_type)
            if isinstance(item, list):
                for thing in item:
                    for t_key in thing:
                        if t_key == 'craftingrequirements':
                            reqs = thing[t_key]
                            if 'craftresource' in reqs:
                                res = reqs['craftresource']
                                item_count += 1
                                print("{} requires resources to craft".format(thing['@uniquename']))
                                if isinstance(res, list):
                                    for r in res:
                                        print('\t{}: {}'.format(r['@count'], r['@uniquename']))
                                else:
                                    print('\t{}: {}'.format(res['@count'], res['@uniquename']))
                            # print(item_type)
    # print(items_json)
    print("{} craftable items found.".format(item_count))

if __name__ == '__main__':
    get_item_data()
