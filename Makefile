.PHONY: check

check:
	ruff format --check .
	ruff check .
	pytest -q

