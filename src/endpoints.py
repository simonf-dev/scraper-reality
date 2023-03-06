from flask import Flask

app = Flask(__name__)


@app.route("/")
def results_page():
    """ Results from the scraped realities"""
    return "Hello, World!"

@app.route("/refresh")
def refresh_results():
    """ Refresh results in the DB"""
    pass


if __name__ == "__main__":
    app.run(debug=True)