ACTIVATE = . ./activate.sh

format:
	$(ACTIVATE) && ruff format src tests

test:
	$(ACTIVATE) && pytest -s tests/

cov:
	$(ACTIVATE) && coverage run -m pytest -s tests && coverage combine && coverage report --show-missing && coverage html

sync:
	$(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt

api:
	$(ACTIVATE) && uvicorn gpt:app --reload --port 8008

build:
	python -m build

deploy:
	twine upload dist/*