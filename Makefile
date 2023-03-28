.PHONY: style
style:
	black src

.PHONY: type-check
type-check:
	env MYPYPATH=src/ mypy --strict --explicit-package-bases src

.PHONY: pylint-check
pylint-check:
	env PYTHONPATH=src/ pylint src

.PHONY: dev-build
dev-build:
	pip3 install -r devel-requirements.in -r requirements.txt

.PHONY: tests
tests:
	pytest src/tests