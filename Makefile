test:
	export DJANGO_SETTINGS_MODULE=tests.settings && pytest

lint:
	ruff check

format:
	ruff format

build:
	python -m pip install --upgrade build
	python -m build

release: build
	python -m pip install --upgrade twine
	python -m twine upload dist/*