""" Middleware for the PostgresAPI"""
from typing import Any, TypedDict, cast, List
import psycopg2
from settings import get_logger

logging = get_logger(__name__)


class EstateFrontendResponse(TypedDict):
    """Structure that's returned back for the frontend view."""

    id: int
    title: str
    place: str
    url: str
    feature: str
    price: int


class EstateDb(TypedDict):
    """Structure that should mirror Estate in PostgresSQL DB"""

    price: int
    title: str
    place: str
    url: str
    has_video: bool


def connect_to_db(
    host: str, database: str, user: str, password: str, port: int
) -> "psycopg2.connection":
    """Wrapper for connection to the DB."""
    connection = psycopg2.connect(
        host=host, database=database, user=user, password=password, port=port
    )
    return connection


def insert_estate_to_db(
    cur: "psycopg2.cursor",
    estate_db: EstateDb,
) -> int:
    """Inserts estate to DB. Returns it's id"""
    logging.debug("Inserting estate %s to DB.", estate_db)
    cur.execute(
        "INSERT INTO estate (title, place, price, url, has_video) VALUES (%s, %s, %s, %s, %s )"
        "RETURNING id;",
        (
            estate_db["title"],
            estate_db["place"],
            estate_db["price"],
            estate_db["url"],
            estate_db["has_video"],
        ),
    )
    returned_response = cur.fetchone()
    if returned_response is None:
        err_msg = "Expected to get id of inserted estate from the DB, but got None"
        logging.error(err_msg)
        raise ValueError(err_msg)
    returned_id = returned_response[0]
    if not isinstance(returned_id, int):
        err_msg = f"Expected to return int from the query, but got : {returned_id}"
        logging.error(err_msg)
        raise ValueError(err_msg)
    logging.debug("Returning id %s for the estate %s", returned_id, estate_db)
    return returned_id


def insert_media_to_db(cur: "psycopg2.cursor", url: str, estate_id: int) -> None:
    """Inserts media record to DB, doesn't commit transaction at the end."""
    cur.execute("INSERT INTO media(url, estate_id) values (%s,%s);", (url, estate_id))
    logging.debug("Inserted media %s for estate %s", url, estate_id)


def insert_or_get_feature(cur: "psycopg2.cursor", label: str) -> int:
    """
    Inserts feature to DB or get existing one with the label. Return it's id
    """
    cur.execute("SELECT id FROM feature WHERE text = %s;", (label,))
    attr_q_res = cur.fetchone()
    if attr_q_res is None:
        cur.execute("INSERT INTO feature (text) VALUES (%s) RETURNING id;", (label,))
        attr_q_res = cur.fetchone()
    if attr_q_res is None or not isinstance(attr_q_res[0], int):
        err_msg = (
            f"Expected to got tuple with single int from the query, "
            f"but got : {attr_q_res}"
        )
        logging.error(err_msg)
        raise ValueError(err_msg)
    logging.debug("Returning id %s for the feature %s", attr_q_res[0], label)
    return attr_q_res[0]


def connect_estate_feature(
    cur: "psycopg2.cursor", estate_id: int, feature_id: int
) -> None:
    """Connects estate with feature and insert this connection to DB."""
    cur.execute(
        "INSERT INTO estate_feature (estate_id, feature_id) VALUES (%s, %s)",
        (estate_id, feature_id),
    )
    logging.debug(
        "Created connection between estate %s and feature %s", estate_id, feature_id
    )


def get_oldest_estates_by_id(cur: "psycopg2.cursor", count: int) -> Any:
    """
    Get {count} last inserted estates to DB.
    """
    logging.info("Getting %s last estates.", count)
    cur.execute(
        "SELECT estate.id, estate.title , estate.place, estate.url, estate.price, "
        "array_to_string(array_agg(distinct media.url), '$'), "
        "array_to_string(array_agg(distinct feature.text), '$'), "
        "estate.has_video from estate JOIN media ON estate.id = media.estate_id "
        "LEFT JOIN estate_feature ON estate.id = estate_feature.estate_id "
        "LEFT JOIN feature ON estate_feature.feature_id = feature.id "
        "GROUP BY 1 ORDER BY id desc LIMIT %s;",
        (count,),
    )
    estates = cur.fetchall()
    logging.debug("Returning last %s last estates %s", count, estates)
    return cast(List[EstateFrontendResponse], estates)


def create_tables(cur: "psycopg2.cursor") -> None:
    """
    Creates tables, if they exist then do nothing. If some error occurs then raises
    psycopg2 exception, see https://www.psycopg.org/docs/errors.html
    Migrations need to be implemented if changing table.
    """
    logging.info("Creating tables for the estates.")
    # Execute a command: this creates a new table
    cur.execute(
        "CREATE TABLE IF NOT EXISTS estate (id SERIAL  PRIMARY KEY,"
        "title varchar (150) NOT NULL,"
        "place varchar (150) NOT NULL,"
        "price int NOT NULL,"
        "has_video boolean NOT NULL,"
        "url varchar (150) NOT NULL,"
        "date_added date DEFAULT CURRENT_TIMESTAMP);"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS  media (id SERIAL  PRIMARY KEY, "
        "url varchar (150) NOT NULL,"
        "estate_id int,"
        "FOREIGN KEY (estate_id) REFERENCES estate (id))"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS feature (id SERIAL  PRIMARY KEY,"
        "text varchar(100) NOT NULL, unique(text))"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS estate_feature (feature_id int ,"
        "estate_id int, FOREIGN KEY (estate_id) REFERENCES estate (id),"
        "FOREIGN KEY (feature_id) REFERENCES feature (id))"
    )
    cur.close()  # type: ignore
    logging.info("Successfullly created all tables for the estates.")
