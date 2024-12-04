import json
import urllib.parse
from typing import List

import requests
from dataclasses import asdict

from data import Price

BASE_URL = 'https://old.west.albion-online-data.com'
API_BASE = '/api/v2/stats'
PRICE_URL = '/Prices'


def get_price(item_ids: List[str]) -> List[Price]:
    id_str = urllib.parse.quote(','.join(item_ids))
    url = BASE_URL + API_BASE + PRICE_URL + '/' + id_str + '.json'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    json_data = response.json()
    if not json_data:
        print("Received an empty or None response")
        return []

    return [Price(**item) for item in json_data]


if __name__ == '__main__':
    item_ids = ['T2_FIBER', 'T3_FIBER']
    prices = get_price(item_ids)
    pricesDicts = [asdict(price) for price in prices]
    print(json.dumps(pricesDicts, indent=4))
