""" Spider classes for parsers"""
import json
import math
from typing import Any, Dict, Iterator, List, cast

import scrapy

from databases import db_proxy as DBProxy
from databases import structures
from settings import SUPPORTED_PROPORTIONS, get_logger

logging = get_logger(__name__)


class EstateSpider(scrapy.Spider):  # type: ignore
    """EstateSpider to parse requests from www.sreality.cz It uses API"""

    web_page = (
        "https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&"
        "page={page}&per_page={per_page}&locality_region_id={region_id}"
    )
    name = "EstateSpider"

    def __init__(self, reality_per_page: int) -> None:
        self.reality_per_page = reality_per_page
        super().__init__()

    def _parse_url(self, estate: Dict["str", Any]) -> str:
        """
        Gets estate API structure and tries to parse url from it by the defined rules.
        Uses SUPPORTED_PROPORTIONS dict, which maps names to values in URL.
        """
        estate_id = estate["_embedded"]["favourite"]["_links"]["self"]["href"].split(
            "/"
        )[-1]
        locality = estate["seo"]["locality"]
        parsed_estate_type = estate["name"].strip().split(" ")[2]
        estate_type = (
            SUPPORTED_PROPORTIONS[parsed_estate_type]
            if parsed_estate_type in SUPPORTED_PROPORTIONS
            else "unknown"
        )
        returned_url = (
            f"https://www.sreality.cz/detail/prodej/"
            f"byt/{estate_type}/{locality}/{estate_id}"
        )
        logging.debug("Returning URL %s", returned_url)
        return returned_url

    def check_images(self, estate: Dict["str", Any], count: int = 3) -> List[str]:
        """
        Checks that images are in correct format and returns first {count} images.
        If there is bad API response from estate, then raises error.
        """
        returned_images = []
        try:
            for image in estate["_links"]["images"][:count]:
                if not isinstance(image["href"], str):
                    raise ValueError(
                        f"Estate image value in API call has wrong type, expected: str, "
                        f"actual type: {type(image['href'])}"
                    )
                returned_images.append(image["href"])
        except (KeyError, IndexError, TypeError) as err:
            err_msg = f"Cannot get {count} images from the estate API structure. Estate: {estate}"
            logging.error(err_msg)
            raise ValueError(err_msg) from err
        logging.debug("Returning links for images: %s", returned_images)
        return returned_images

    def check_labels(self, estate: Dict[str, Any]) -> List[str]:
        """
        Checks that API labels are in correct format and returns them.
        If there is bad API response, then raises error.
        """
        try:
            for label in estate["labels"]:
                if not isinstance(label, str):
                    raise ValueError(
                        f"Estate label value in API call has wrong type, expected: str, "
                        f"actual type: {type(label)}"
                    )
        except (KeyError, IndexError, TypeError) as err:
            err_msg = (
                f"Cannot get labels from the estate API structure. Estate: {estate}"
            )
            logging.error(err_msg)
            raise ValueError(err_msg) from err
        logging.debug("Returning features: %s", estate["labels"])
        return cast(List[str], estate["labels"])

    def check_estate(self, estate: Dict[str, Any]) -> structures.EstateDb:
        """
        Checks that API response is in correct format (its EstateDb part)
         and returns TypedDict structure which mirrors estate structure in DB
        """
        try:
            if not isinstance(estate["price"], int):
                raise ValueError(
                    f"Estate price value in API call has wrong type, expected: int, "
                    f"actual value: {type(estate['price'])}"
                )
            for key in ["name", "locality"]:
                if not isinstance(estate[key], str):
                    raise ValueError(
                        f"Estate {key} value in API call has wrong type, expected type: str, "
                        f"actual value: {type(estate[key])}"
                    )
            if not isinstance(estate["has_video"], bool):
                raise ValueError(
                    f"Estate has_video value in API call has wrong type, expected: str, "
                    f"actual type: {type(estate['has_video'])}"
                )
            estate_url = self._parse_url(estate)
        except (KeyError, IndexError, ValueError, TypeError) as err:
            err_msg = f"Estate API response doesn't have proper values. Estate value: {estate}"
            logging.error(err_msg)
            raise ValueError(err_msg) from err
        returned_struct: structures.EstateDb = {
            "price": estate["price"],
            "url": estate_url,
            "place": estate["locality"],
            "title": estate["name"],
            "has_video": estate["has_video"],
            "medias": [],
            "region": 0,
            "features": [],
        }
        logging.debug("Checked estate and returning %s", returned_struct)
        return returned_struct

    def write_to_db(self, estates: List[Dict[str, Any]], region: int) -> None:
        """
        Gets estates API response and tries to parse them and saves them to DB.
        """
        logging.info("Writing to DB %s estates.", len(estates))
        estates_db = []
        for estate in estates:
            try:
                estate_db = self.check_estate(estate)
                images = self.check_images(estate)
                labels = self.check_labels(estate)
            except ValueError:
                err_msg = (
                    f"Failed to parse {estate} estate into DB. Continuing with others."
                )
                logging.error(err_msg)
                continue
            estate_db["medias"] = images
            estate_db["features"] = labels
            estate_db["region"] = region
            estates_db.append(estate_db)
        DBProxy.insert_estates_to_db(estates_db)
        logging.info("Successfully wrote %s estates to DB", len(estates))

    def start_requests(self, reality_count: int = 500) -> Iterator[scrapy.Request]:
        """
        Method that starts to iterate requests for estates. Needed for async.
        """
        logging.info(
            "Starting requests with reality_count %s and reality per page %s",
            reality_count,
            self.reality_per_page,
        )
        iterations = math.ceil(reality_count / self.reality_per_page) + 1
        # need to make correct number of iterations in edge cases
        if reality_count % self.reality_per_page != 0:
            iterations += 1
        for page in range(1, reality_count // self.reality_per_page):
            for region in range(1, 15):
                yield scrapy.Request(
                    url=self.web_page.format(
                        per_page=self.reality_per_page, page=page, region_id=region
                    ),
                    callback=self.parse,
                )

    def parse(self, response: Any, **kwargs: Any) -> None:
        """
        Tries to parse response and save it to DB. If there is an exception, it's caught by
        methods level above or by methods level below.
        """
        json_object = json.loads(response.body)
        try:
            region = int(json_object["filter"]["locality_region_id"])
        except (KeyError, IndexError, ValueError, TypeError) as err:
            err_msg = (
                f"Cannot get region from the API response. Response: {json_object}"
            )
            logging.error(err_msg)
            raise ValueError(err_msg) from err
        self.write_to_db(json_object["_embedded"]["estates"], region)
