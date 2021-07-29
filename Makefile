init:
	poetry install
	poetry plugin add poetry-version-plugin
	poetry run pre-commit install

test:
	poetry run py.test --capture=no --cov-report term-missing --cov-report html --cov=djet testproject/
	poetry run flake8 .

migrate:
	poetry run python testproject/manage.py migrate

runserver:
	poetry run python testproject/manage.py runserver
