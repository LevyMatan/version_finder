.PHONY: test coverage format lint clean install install-dev

install:
	@echo "Choose an installation option:"
	@echo "1. Only core"
	@echo "2. Core + CLI"
	@echo "3. Core + GUI"
	@echo "4. Core + GUI + CLI"
	@read -p "Enter your choice [1-4]: " choice; \
	case $$choice in \
		1) pip install . ;; \
		2) pip install .[cli] ;; \
		3) pip install .[gui] ;; \
		4) pip install .[cli+gui] ;; \
		*) echo "Invalid choice. Exiting."; exit 1 ;; \
	esac

install-dev:
	pip install -e .[all]

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
