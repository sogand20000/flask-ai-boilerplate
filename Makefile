.PHONY: run lint format test clean

run:
	python -m src.app

lint:
	ruff check .

format:
	ruff format .

check: format lint