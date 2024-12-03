.PHONY: test coverage format lint clean install install-dev uninstall

tree:
	tree -L 4 -I "version_finder_env" -I "__pycache__" -I "*.egg-info"

install-core:
	pip install core/

install-cli:
	make install-core
	pip install cli/

install-gui:
	make install-core
	pip install gui/

install-dev:
	pip install -e core/[dev]
	pip install -e cli/
	pip install -e gui/


install:
	@echo "Choose an installation option:"
	@echo "1. Only core"
	@echo "2. Core + CLI"
	@echo "3. Core + GUI"
	@echo "4. Core + GUI + CLI"
	@read -p "Enter your choice [1-4]: " choice; \
	case $$choice in \
		1) make install-core ;; \
		2) make install-cli ;; \
		3) make install-gui ;; \
		4) make install-gui && make install-cli ;; \
		*) echo "Invalid choice. Exiting."; exit 1 ;; \
	esac

test-core:
	cd core && pytest -n auto

test-cli:
	cd cli && pytest -n auto

test-gui:
	cd gui && pytest -n auto

test:
	pytest -n auto

coverage:
# Run tests and generate coverage report
# Run on core, cli and gui
	pytest --cov=core/src --cov=cli/src --cov=gui/src --cov-report term-missing --cov-report html
	@echo "HTML coverage report generated in htmlcov/index.html"

format:
	autopep8 --in-place --recursive .

lint:
	flake8 .

clean:
	find . -type d \( -name ".venv" -prune \) -o -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d \( -name ".venv" -prune \) -o -type d -name "build" -exec rm -rf {} +
	find . -type d \( -name ".venv" -prune \) -o -type d -name "dist" -exec rm -rf {} +
	find . -type d \( -name ".venv" -prune \) -o -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage

uninstall:
	pip uninstall -y version-finder-git-based-versions
	pip uninstall -y version-finder-git-based-versions-cli
	pip uninstall -y version-finder-git-based-versions-gui-app
	make clean