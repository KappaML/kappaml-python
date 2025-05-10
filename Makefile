install:
	pip install --upgrade pip build twine

build:
	python -m build

release:
	python -m twine upload dist/*