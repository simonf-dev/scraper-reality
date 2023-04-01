""" Endpoints for the whole app"""
import random
from typing import Union

from flask import Flask, render_template, request

import constants as const
from databases import db_proxy as DBProxy
from settings import get_logger, APP_PORT

app = Flask(__name__)
logging = get_logger(__name__)


@app.route("/")
def results_page() -> Union[tuple[str, int], str]:
    """Results from the scraped realities"""
    region = request.args.get("region")
    try:
        region_int = (
            int(region)
            if region is not None
            else random.randint(*const.get_region_spread())
        )
    except ValueError:
        return "Bad format of the region param.", 400
    if (
        region_int < const.get_region_spread()[0]
        or region_int > const.get_region_spread()[1]
    ):
        return "Region is not in the range.", 400
    estates = DBProxy.get_oldest_estates_for_region(region_int, 200)
    logging.info("Sending response back to %s", request.access_route)
    return render_template(
        "index.html",
        estates=estates,
        regions=const.REGION_MAPPING,
        selected_region=const.REGION_MAPPING[region_int],
    )


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=APP_PORT)

