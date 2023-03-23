""" Init scripts that will be executed at the each start of container"""
import psycopg2
from scrapy.crawler import CrawlerProcess

import db_api as PostgresAPI
from settings import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    get_logger,
    POSTGRES_PORT
)
from spiders import EstateSpider

logging = get_logger(__name__)


def parse_actual_estates(
    con: "psycopg2.connection", reality_per_page: int = 20
) -> None:
    """Parse www.sreality.cz estates to the DB."""
    logging.info(
        "Starting to initialize crawler with reality_per_page %s", reality_per_page
    )
    process = CrawlerProcess(
        {"USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"}
    )
    process.crawl(EstateSpider, con, reality_per_page=reality_per_page)
    process.start()


if __name__ == "__main__":
    #  Creates connection with DB for all init scripts
    logging.info("Running initial scripts for the application.")
    connection = PostgresAPI.connect_to_db(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT
    )
    PostgresAPI.create_tables(connection.cursor())
    parse_actual_estates(connection)
    connection.close()
