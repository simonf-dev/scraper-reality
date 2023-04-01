""" Middleware for the PostgresAPI"""
from typing import Any, List

from pymongo import MongoClient
from pymongo.database import Database

from databases import structures
from settings import (
    MONGO_CONNECTION_STRING,
    MONGO_HOST,
    MONGO_PASSWORD,
    MONGO_USER,
    get_logger,
)

logging = get_logger(__name__)


def connect_to_db() -> Database[Any]:
    """
    Wrapper for connection to the DB. User and password are taken from env variables.
    If MONGO_CONNECTION_STRING is set, it's used instead of user and password.
    """
    connection_string = MONGO_CONNECTION_STRING
    if connection_string is None:
        connection_string = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}"
    logging.info("Connecting to DB with connection string %s", connection_string)
    client: MongoClient[Any] = MongoClient(connection_string)

    return client["scraper"]


def init_db(connection_db: Database[Any] = connect_to_db()) -> None:
    """Creates DB collections. Creates index on 'region'."""
    if "estates" in connection_db.list_collection_names():
        logging.info("Collection 'estates' exists! Not creating it.")
    else:
        connection_db.create_collection("estates")
    estates_collection = connection_db["estates"]
    if "region" in estates_collection.index_information():
        logging.info("Index 'region' exists! Not creating it.")
        return
    estates_collection.create_index("region")


def insert_estates_to_db(
    estates: List[structures.EstateDb], connection_db: Database[Any] = connect_to_db()
) -> None:
    """Inserts estates to DB. Creates index on 'region' if it doesn't exist."""
    estates_collection = connection_db["estates"]
    estates_collection.insert_many(estates)
    if "region" in estates_collection.index_information():
        logging.info("Index 'region' exists! Not creating it.")
        return
    estates_collection.create_index("region")


def get_oldest_estates_for_region(
    region: int, limit: int, connection_db: Database[Any] = connect_to_db()
) -> List[structures.EstateFrontendResponse]:
    """Returns oldest estates for region."""
    estates = (
        connection_db["estates"].find({"region": region}).sort("_id", 1).limit(limit)
    )
    return list(estates)
