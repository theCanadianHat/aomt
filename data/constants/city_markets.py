from enum import Enum, auto
from typing import Optional


class CityMarkets(Enum):
    LYM = auto()
    MART = auto()
    BRIDGE = auto()
    THET = auto()
    FS = auto()
    BM = auto()
    CAR = auto()
    BRE = auto()
    UNKNOWN = auto()

    def __init__(self, _):
        properties = {
            'UNKNOWN': ('Unknown', 'Unknown', False),
            'LYM': ('Lymhurst', 'Lymhurst', False),
            'MART': ('Martlock', 'Martlock', False),
            'BRIDGE': ('Bridgewatch', 'Bridgewatch', False),
            'THET': ('Thetford', 'Thetford', False),
            'FS': ('Fort Sterling', 'Fort Sterling', False),
            'BM': ('Black Market', 'Black Market', True),
            'CAR': ('Caerleon', 'Caerleon', True),
            'BRE': ('5003', 'Brecilien', True)
        }
        self.city_key, self.city_name, self.pvp = properties[self.name]

    @classmethod
    def get_by_city_key(cls, key) -> Optional['CityMarkets']:
        for member in cls:
            if member.city_key == key:
                return member
        return None
