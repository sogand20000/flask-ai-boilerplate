.PHONY: run lint format test clean

run:
	PYTHONPATH=backend python -m backend.src.app
lint:
	ruff check .

format:
	ruff format .

check: format lint