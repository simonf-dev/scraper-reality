""" Endpoints for the whole app"""
from flask import Flask, render_template, request

import db_api as PostgresAPI
from settings import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    get_logger,
)

app = Flask(__name__)
CONNECTION = PostgresAPI.connect_to_db(
    host=POSTGRES_HOST,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
)
logging = get_logger(__name__)


@app.route("/")
def results_page() -> str:
    """Results from the scraped realities"""
    cur = CONNECTION.cursor()
    estates = PostgresAPI.get_oldest_estates_by_id(cur, 500)
    estates_html = [
        {
            "name": estate[1],
            "place": estate[2],
            "url": estate[3],
            "price": estate[4],
            "images": estate[5].strip().split("$"),
            "attributes": estate[6].strip().split("$"),
            "has_video": estate[7],
        }
        for estate in estates
    ]
    logging.info("Sending response back to %s", request.access_route)
    cur.close()  # type: ignore
    return render_template("index.html", estates=estates_html)


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
