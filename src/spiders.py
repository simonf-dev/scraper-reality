import logging

import scrapy
import math
from scrapy.crawler import CrawlerProcess
import json
import psycopg2
from settings import  POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB, SUPPORTED_PROPORTIONS
class RealitySpider(scrapy.Spider):
    reality_offers_count = 20

    web_page = "https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&page={page}&per_page={per_page}"
    name = 'realityspider'
    def parse_url(self, estate) -> str:
        estate_id = estate["_embedded"]["favourite"]["_links"]["self"]["href"].split("/")[-1]
        locality = estate["seo"]["locality"]
        parsed_flat_type = estate["name"].strip().split(" ")[2]
        flat_type = SUPPORTED_PROPORTIONS[parsed_flat_type] if parsed_flat_type in SUPPORTED_PROPORTIONS else "unknown"
        return f"https://www.sreality.cz/detail/prodej/byt/{flat_type}/{locality}/{estate_id}"

    def check_estate(self, estate) -> None:
        """ Checks that esponse API response is in correct format."""
        try:
            if not isinstance(estate["price"], int):
                raise ValueError(f"Estate price value in API call has wrong value, expected: int, "
                                 f"actual value: {estate['price']}")
            for key in ["name", "locality"]:
                if not isinstance(estate[key], str):
                    raise ValueError(f"Estate {key} value in API call has wrong value, expected type: str, "
                                     f"actual value: {estate[key]}")
            for image in estate["_links"]["images"][:3]:
                if not isinstance(image["href"], str):
                    raise ValueError(f"Estate image value in API call has wrong value, expected: str, "
                                     f"actual value: {estate['price']}")
            if not isinstance(estate["has_video"], bool):
                raise ValueError(f"Estate has_video value in API call has wrong value, expected: str, "
                                 f"actual value: {estate['price']}")
        except KeyError as e:
            raise ValueError("Estate API response doesn't have proper values.") from e

    def write_to_db(self, estates):
        conn = psycopg2.connect(
            host=POSTGRES_HOST, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD
        )
        cur = conn.cursor()
        for estate in estates:
            self.check_estate(estate)
            cur.execute("INSERT INTO flat (title, place, price, url, has_video) VALUES (%s, %s, %s, %s, %s )"
                        "RETURNING id;"
                        ,(estate["name"], estate["locality"], estate["price"], self.parse_url(estate),
                          estate["has_video"]))
            flat_id = cur.fetchone()[0]
            for index, image in enumerate(estate["_links"]["images"][:3]):
                cur.execute("INSERT INTO media(url, flat_id) values (%s,%s);",
                            (image["href"], flat_id))
            for index, label in enumerate(estate["labels"]):
                logging.warning(label)
                cur.execute("SELECT id FROM reality_attribute WHERE text = %s;", (label,))
                attr_q_res = cur.fetchone()
                if attr_q_res is None:
                    cur.execute("INSERT INTO reality_attribute (text) VALUES (%s) RETURNING id;", (label,))
                    attr_q_res = cur.fetchone()
                attr_id = attr_q_res[0]
                cur.execute("INSERT INTO attribute_flat (flat_id, attribute_id) VALUES (%s, %s)",
                            (flat_id, attr_id))

        conn.commit()
        conn.close()


    def start_requests(self, reality_count: int = 500):
        for page in range(1, reality_count // self.reality_offers_count):
            yield scrapy.Request(url=self.web_page.format(per_page=self.reality_offers_count, page=page), callback=self.parse)

    def parse(self, response):
        json_object = json.loads(response.body)
        self.write_to_db(json_object["_embedded"]["estates"])


if __name__ == '__main__':

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(RealitySpider)
    process.start()