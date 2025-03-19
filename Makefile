test:
	export DJANGO_SETTINGS_MODULE=tests.settings && pytest

lint:
	ruff check

format:
	ruff format
