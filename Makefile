install:
	pip install --upgrade pip build twine

build:
	rm -rf dist
	python -m build

release:
	python -m twine upload dist/*