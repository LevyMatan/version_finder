.PHONY: test coverage format lint clean

test:
	pytest

coverage:
	pytest --cov=./src --cov-report term-missing --cov-report html
	@echo "HTML coverage report generated in htmlcov/index.html"

format:
	autopep8 --in-place --recursive .

lint:
	flake8 .

clean:
	rm -rf htmlcov/
	rm -f .coverage
