.PHONY: test coverage format lint clean install install-dev uninstall

# Detect OS
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

tree:
ifeq ($(DETECTED_OS),Windows)
	@echo "Listing directory structure..."
	@powershell -Command "Get-ChildItem -Recurse -Depth 4 | Where-Object { $$_.Name -notmatch 'version_finder_env|__pycache__|\.egg-info$$' } | Select-Object FullName"
else
	tree -L 4 -I "version_finder_env" -I "__pycache__" -I "*.egg-info"
endif

install-core:
	pip install core/

install-cli:
	$(MAKE) install-core
	pip install cli/

install-gui:
	$(MAKE) install-core
	pip install gui/

install-dev:
	pip install -e core/[dev]
	pip install -e cli/
	pip install -e gui/

commit-parser:
	pip install -e custom_scope_commit_parser/

install:
ifeq ($(DETECTED_OS),Windows)
	@echo "Choose an installation option:"
	@echo "1. Only core"
	@echo "2. Core + CLI"
	@echo "3. Core + GUI"
	@echo "4. Core + GUI + CLI"
	@powershell -Command "$$choice = Read-Host 'Enter your choice [1-4]'; \
	switch ($$choice) { \
		1 { $(MAKE) install-core } \
		2 { $(MAKE) install-cli } \
		3 { $(MAKE) install-gui } \
		4 { $(MAKE) install-gui; $(MAKE) install-cli } \
		default { Write-Host 'Invalid choice. Exiting.'; exit 1 } \
	}"
else
	@echo "Choose an installation option:"
	@echo "1. Only core"
	@echo "2. Core + CLI"
	@echo "3. Core + GUI"
	@echo "4. Core + GUI + CLI"
	@read -p "Enter your choice [1-4]: " choice; \
	case $$choice in \
		1) $(MAKE) install-core ;; \
		2) $(MAKE) install-cli ;; \
		3) $(MAKE) install-gui ;; \
		4) $(MAKE) install-gui && $(MAKE) install-cli ;; \
		*) echo "Invalid choice. Exiting."; exit 1 ;; \
	esac
endif

test-core:
	pytest core -n auto

test-cli:
	pytest cli -n auto

test-gui:
	pytest gui -n auto

test:
	$(MAKE) test-core
	$(MAKE) test-cli
	$(MAKE) test-gui

cov-gui:
	pytest gui --cov=gui/src --cov-report term-missing --cov-report html

cov-core:		
	pytest core --cov=core/src --cov-report term-missing --cov-report html

cov-cli:
	pytest cli --cov=cli/src --cov-report term-missing --cov-report html

cov-combine:
	coverage erase
	pytest gui --cov=gui/src --cov-append
	pytest core --cov=core/src --cov-append
	pytest cli --cov=cli/src --cov-append
	coverage report
	coverage html
	
format:
	autopep8 --in-place --recursive .

lint:
	flake8 .

clean:
ifeq ($(DETECTED_OS),Windows)
	@powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Include '__pycache__','build','dist','*.egg-info' | Where-Object { $$_.FullName -notmatch '\.venv' } | Remove-Item -Recurse -Force"
	@powershell -Command "if (Test-Path htmlcov) { Remove-Item -Recurse -Force htmlcov }"
	@powershell -Command "if (Test-Path .coverage) { Remove-Item -Force .coverage }"
else
	find . -type d \( -name ".venv" -prune \) -o -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d \( -name ".venv" -prune \) -o -type d -name "build" -exec rm -rf {} +
	find . -type d \( -name ".venv" -prune \) -o -type d -name "dist" -exec rm -rf {} +
	find . -type d \( -name ".venv" -prune \) -o -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage
endif

uninstall:
	pip uninstall -y version-finder-git-based-versions-gui-app
	pip uninstall -y version-finder-git-based-versions-cli
	pip uninstall -y version-finder-git-based-versions
	$(MAKE) clean