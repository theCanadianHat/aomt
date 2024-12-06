from dataclasses import dataclass, field

from data.constants.city_markets import CityMarkets


@dataclass
class Price:
    item_id: str
    city: str
    quality: int
    sell_price_min: int
    sell_price_min_date: str
    sell_price_max: int
    sell_price_max_date: str
    buy_price_min: int
    buy_price_min_date: str
    buy_price_max: int
    buy_price_max_date: str
    city_market: CityMarkets = field(default=CityMarkets.UNKNOWN)

    def __post_init__(self):
        mapped_city = CityMarkets.get_by_city_key(self.city)
        if mapped_city:
            self.city_market = mapped_city


