# scraper-reality
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
5. Frontend improvement