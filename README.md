# scraper-reality
## Description
It's task for the interview with task:
Use scrapy framework to scrape the first 500 items (title, image url) from sreality.cz (flats, sell) and save it in the Postgresql database. Implement a simple HTTP server in python and show these 500 items on a simple page (title and image) and put everything to single docker-compose command so that I can just run "docker-compose up" in the Github repository and see the scraped ads on http://127.0.0.1:8080 page

It took 12 hours to make it.

## How to use
1. App can be started with commands:
`docker compose build && docker-compose up`
2. If you want to develop or try checks (Linux):
`python3 -m venv venv && source venv/bin/activate && make dev-build`
3. Check Makefile for possible checks

If I had more time, I'd finish this list of things:
1. Unit tests and E2E tests
2. Improve exception handling.
3. API checking using schema packages
4. Data re-reading (possibility to clean DB)
5. Frontend improvement (video sign, whole page reformatting)
6. Mask Postgres password for production
7. Add variable count of estates per page / paging
