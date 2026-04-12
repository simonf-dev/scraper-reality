# scraper-reality

A timed interview project, completed in 12 hours. Containerized, PostgreSQL-backed, and fully working end-to-end.

## Task

Scrape the first 500 flat listings (title, image URL) from sreality.cz, store them in PostgreSQL, and serve them through a simple Python HTTP server — all wired up so a single `docker-compose up` is enough to see results at http://127.0.0.1:8080.

Another ~4 hours took to implement NoSQL database to the project, which you can see in pull requests. Live NoSQL version should run on:
https://frontend-scraper.azurewebsites.net

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
