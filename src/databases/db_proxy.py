"""
This module is a proxy for DBs.
It is used to hide DBs implementation details from other modules.
"""
from typing import List

from databases import nosql_api as NoSQLAPI
from databases import structures


def init_dbs() -> None:
    """Initializes DBs. Right now there is only NoSQLAPI used"""
    NoSQLAPI.init_db()


def insert_estates_to_db(estates: List[structures.EstateDb]) -> None:
    """Inserts estates to DB."""
    NoSQLAPI.insert_estates_to_db(estates)


def get_oldest_estates_for_region(
    region: int, limit: int
) -> List[structures.EstateFrontendResponse]:
    """Returns oldest estates for region."""
    return NoSQLAPI.get_oldest_estates_for_region(region, limit)
