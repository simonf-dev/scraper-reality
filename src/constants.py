""" Constants for the project. Including mapping between ids and names etc."""
from functools import lru_cache
from typing import Tuple

REGION_MAPPING = {
    1: "Jihočeský kraj",
    2: "Plzeňský kraj",
    3: "Karlovarský kraj",
    4: "Ústecký kraj",
    5: "Liberecký kraj",
    6: "Královehradecký kraj",
    7: "Pardubický kraj",
    8: "Olomoucký kraj",
    9: "Zlínský kraj",
    10: "Hlavní město Praha",
    11: "Středočeský kraj",
    12: "Moravskoslezský kraj",
    13: "Vysočina",
    14: "Jihomoravský kraj",
}


@lru_cache(maxsize=None)
def get_region_spread() -> Tuple[int, int]:
    """Get region spread for the app."""
    return min(REGION_MAPPING.keys()), max(REGION_MAPPING.keys())
