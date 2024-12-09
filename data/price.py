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
            self.city = self.city_market.city_name

    def __str__(self):
        return f"""Price(
    item_id={self.item_id},
    city={self.city}, 
    sell_price_min={self.sell_price_min}, 
    sell_price_max={self.sell_price_max}, 
    buy_price_min={self.buy_price_min},
    buy_price_max={self.sell_price_max}
)"""

    def __repr__(self):
        return self.__str__()
