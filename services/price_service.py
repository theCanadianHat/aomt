import json
import sys
from typing import List

from dataclasses import asdict

from aodp.api import get_price
from data import Price

DEBUG = False


def __get_item_price(item_ids: List[str]) -> List[Price] | None:
    api_prices = get_price(item_ids)

    if api_prices is None:
        print("Received None from get_price")
        return None

    if not api_prices:
        print("Received an empty list from get_price")
        return None

    return api_prices


def __get_min_sell_price_min(prices: List[Price]) -> List[Price]:
    lowest_found = []
    lowest_value = int(sys.maxsize)

    for price in prices:
        if price.sell_price_min < lowest_value and price.sell_price_min != 0:
            lowest_value = price.sell_price_min
            lowest_found.append(price)

    for lp in lowest_found:
        if lp.sell_price_min != lowest_value:
            lowest_found.remove(lp)

    return lowest_found


def get_city_with_lowest_sell_price(item_ids: List[str]) -> List[Price] | None:
    low_prices = sorted(__get_item_price(item_ids), key=lambda p: p.sell_price_min)

    lowest = __get_min_sell_price_min(low_prices)

    if DEBUG:
        prices_dicts = [asdict(price) for price in low_prices if price is not None]
        print(json.dumps(prices_dicts, indent=4))

    return lowest


def get_safe_city_with_lowest_sell_price(item_ids: List[str]) -> List[Price] | None:
    low_prices = sorted(__get_item_price(item_ids), key=lambda price: price.sell_price_min)
    safe_prices = list(filter(lambda p: not p.city_market.pvp, low_prices))

    lowest = __get_min_sell_price_min(safe_prices)

    if DEBUG:
        prices_dicts = [asdict(price) for price in safe_prices if price is not None]
        print(json.dumps(prices_dicts, indent=4))

    return lowest


def __get_max_buy_price_max(prices: List[Price]) -> List[Price]:
    highest_found = []
    highest_value = int(-sys.maxsize)

    for price in prices:
        if price.buy_price_max > highest_value and price.buy_price_max != 0:
            highest_value = price.buy_price_max
            highest_found.append(price)

    for hp in highest_found:
        if hp.buy_price_max != highest_value:
            highest_found.remove(hp)

    return highest_found


def get_city_with_highest_buy_price(item_ids: List[str]) -> List[Price] | None:
    prices = sorted(__get_item_price(item_ids), key=lambda price: price.buy_price_max, reverse=True)

    highest = __get_max_buy_price_max(prices)

    if DEBUG:
        prices_dicts = [asdict(price) for price in prices if price is not None]
        print(json.dumps(prices_dicts, indent=4))

    return highest


def get_safe_city_with_highest_buy_price(item_ids: List[str]) -> List[Price] | None:
    high_prices = sorted(__get_item_price(item_ids), key=lambda price: price.buy_price_max, reverse=True)
    safe_prices = list(filter(lambda p: not p.city_market.pvp, high_prices))

    lowest = __get_max_buy_price_max(safe_prices)

    if DEBUG:
        prices_dicts = [asdict(price) for price in safe_prices if price is not None]
        print(json.dumps(prices_dicts, indent=4))

    return lowest


if __name__ == '__main__':
    item = 'T2_FIBER'
    buy_from = get_city_with_lowest_sell_price([item])
    sell_to = get_city_with_highest_buy_price([item])

    if not buy_from or not sell_to:
        print('Missing a buyer or seller')
        exit(1)

    if len(buy_from) == 1 and len(sell_to) == 1:
        buy = buy_from[0]
        sell = sell_to[0]
        print("Buy {} form {} for {}".format(item, buy.city_market.city_name, buy.sell_price_min))
        print("Buy {} form {} for {}".format(item, sell.city_market.city_name, sell.buy_price_max))

        profit = sell.buy_price_max - buy.sell_price_min
        roi = profit / buy.sell_price_min
        print('This will net you {} with an ROI of {}'.format(profit, roi))

    buy_from = get_safe_city_with_lowest_sell_price([item])
    sell_to = get_safe_city_with_highest_buy_price([item])

    if not buy_from or not sell_to:
        print('Missing a buyer or seller')
        exit(1)

    if len(buy_from) == 1 and len(sell_to) == 1:
        buy = buy_from[0]
        sell = sell_to[0]
        print("Buy {} form {} for {}".format(item, buy.city_market.city_name, buy.sell_price_min))
        print("Buy {} form {} for {}".format(item, sell.city_market.city_name, sell.buy_price_max))

        profit = sell.buy_price_max - buy.sell_price_min
        roi = profit / buy.sell_price_min
        print('This will net you {} with an ROI of {}'.format(profit, roi))
