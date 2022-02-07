all: check test

fmt:
	poetry run black src tests

check:
	poetry run mypy src tests

test:
	poetry run pytest

install:
	poetry install

clean:
	poetry env list | awk '{print $$1}' | xargs -I {} poetry env remove {}
	rm poetry.lock
