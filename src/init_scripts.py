""" Init scripts that will be executed at the each start of container"""
from scrapy.crawler import CrawlerProcess

from databases import db_proxy as DbProxy
from settings import (
    get_logger,
)
from spiders import EstateSpider

logging = get_logger(__name__)


def parse_actual_estates(
    reality_per_page: int = 20
) -> None:
    """Parse www.sreality.cz estates to the DB."""
    logging.info(
        "Starting to initialize crawler with reality_per_page %s", reality_per_page
    )
    process = CrawlerProcess(
        {"USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"}
    )
    process.crawl(EstateSpider, reality_per_page=reality_per_page)
    process.start()


if __name__ == "__main__":
    #  Creates connection with DB for all init scripts
    logging.info("Running initial scripts for the application.")
    DbProxy.init_dbs()
    parse_actual_estates()
    logging.info("Finished running initial scripts for the application.")
