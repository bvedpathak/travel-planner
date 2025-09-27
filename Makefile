# Travel Planner - Comprehensive Code Quality and Analysis Makefile
#
# This Makefile provides commands for running various code quality tools,
# static analysis, security checks, and generating reports.

.PHONY: help install lint format type-check security test complexity dead-code \
        docstring-coverage vulnerability-scan all-checks clean reports \
        sonar-scan pre-commit-install ci-local

# Default Python and source directories
PYTHON = python3
PIP = pip3
SRC_DIRS = core services tools tools_solid server.py server_solid.py
TEST_DIRS = tests
REPORTS_DIR = reports

# Colors for output
BOLD = \033[1m
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
RESET = \033[0m

help: ## Show this help message
	@echo "$(BOLD)Travel Planner - Code Quality Tools$(RESET)"
	@echo ""
	@echo "$(BOLD)Setup Commands:$(RESET)"
	@echo "  install                 Install all development dependencies"
	@echo "  pre-commit-install      Install pre-commit hooks"
	@echo ""
	@echo "$(BOLD)Code Quality Commands:$(RESET)"
	@echo "  format                  Format code with black and isort"
	@echo "  lint                    Run all linting tools (pylint, flake8)"
	@echo "  type-check              Run type checking with mypy"
	@echo "  security                Run security analysis with bandit"
	@echo "  test                    Run tests with coverage"
	@echo ""
	@echo "$(BOLD)Analysis Commands:$(RESET)"
	@echo "  complexity              Analyze code complexity"
	@echo "  dead-code               Find dead/unused code"
	@echo "  docstring-coverage      Check docstring coverage"
	@echo "  vulnerability-scan      Scan for known vulnerabilities"
	@echo ""
	@echo "$(BOLD)Comprehensive Commands:$(RESET)"
	@echo "  all-checks              Run all quality checks"
	@echo "  reports                 Generate comprehensive reports"
	@echo "  sonar-scan              Run SonarQube analysis"
	@echo "  ci-local                Simulate CI pipeline locally"
	@echo ""
	@echo "$(BOLD)Utility Commands:$(RESET)"
	@echo "  clean                   Clean temporary files and reports"

# Setup Commands
install: ## Install all development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)✅ Dependencies installed successfully$(RESET)"

pre-commit-install: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(RESET)"
	pre-commit install
	@echo "$(GREEN)✅ Pre-commit hooks installed$(RESET)"

# Code Quality Commands
format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code with black...$(RESET)"
	black $(SRC_DIRS)
	@echo "$(BLUE)Sorting imports with isort...$(RESET)"
	isort $(SRC_DIRS)
	@echo "$(GREEN)✅ Code formatted successfully$(RESET)"

format-check: ## Check if code formatting is correct
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	black --check $(SRC_DIRS) || (echo "$(RED)❌ Code formatting issues found$(RESET)" && exit 1)
	isort --check-only $(SRC_DIRS) || (echo "$(RED)❌ Import sorting issues found$(RESET)" && exit 1)
	@echo "$(GREEN)✅ Code formatting is correct$(RESET)"

lint: ## Run all linting tools
	@echo "$(BLUE)Running pylint...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	pylint $(SRC_DIRS) --output-format=text --reports=yes > $(REPORTS_DIR)/pylint-report.txt || true
	@echo "$(BLUE)Running flake8...$(RESET)"
	flake8 $(SRC_DIRS) --output-file=$(REPORTS_DIR)/flake8-report.txt || true
	@echo "$(GREEN)✅ Linting completed (check $(REPORTS_DIR)/ for detailed reports)$(RESET)"

lint-strict: ## Run linting with strict settings (fail on any issues)
	@echo "$(BLUE)Running strict linting...$(RESET)"
	pylint $(SRC_DIRS) --fail-under=8.0
	flake8 $(SRC_DIRS)
	@echo "$(GREEN)✅ Strict linting passed$(RESET)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running mypy type checking...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	mypy $(SRC_DIRS) --html-report $(REPORTS_DIR)/mypy-html --txt-report $(REPORTS_DIR)/mypy-txt || true
	@echo "$(GREEN)✅ Type checking completed (check $(REPORTS_DIR)/ for reports)$(RESET)"

type-check-strict: ## Run type checking with strict settings
	@echo "$(BLUE)Running strict type checking...$(RESET)"
	mypy $(SRC_DIRS) --strict
	@echo "$(GREEN)✅ Strict type checking passed$(RESET)"

security: ## Run security analysis with bandit
	@echo "$(BLUE)Running bandit security analysis...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	bandit -r $(SRC_DIRS) -f json -o $(REPORTS_DIR)/bandit-report.json || true
	bandit -r $(SRC_DIRS) -f txt -o $(REPORTS_DIR)/bandit-report.txt || true
	@echo "$(GREEN)✅ Security analysis completed$(RESET)"

security-strict: ## Run security analysis with strict settings
	@echo "$(BLUE)Running strict security analysis...$(RESET)"
	bandit -r $(SRC_DIRS) --severity-level medium
	@echo "$(GREEN)✅ Strict security analysis passed$(RESET)"

test: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	pytest --cov=$(SRC_DIRS) --cov-report=html:$(REPORTS_DIR)/coverage-html --cov-report=xml:$(REPORTS_DIR)/coverage.xml --cov-report=term
	@echo "$(GREEN)✅ Tests completed$(RESET)"

# Analysis Commands
complexity: ## Analyze code complexity
	@echo "$(BLUE)Analyzing code complexity with radon...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	radon cc $(SRC_DIRS) --show-complexity --min B --json > $(REPORTS_DIR)/complexity.json
	radon cc $(SRC_DIRS) --show-complexity --min B > $(REPORTS_DIR)/complexity.txt
	@echo "$(BLUE)Running xenon complexity analysis...$(RESET)"
	xenon --max-absolute B --max-modules B --max-average A $(SRC_DIRS) || true
	@echo "$(GREEN)✅ Complexity analysis completed$(RESET)"

dead-code: ## Find dead/unused code
	@echo "$(BLUE)Finding dead code with vulture...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	vulture $(SRC_DIRS) > $(REPORTS_DIR)/dead-code.txt || true
	@echo "$(GREEN)✅ Dead code analysis completed$(RESET)"

docstring-coverage: ## Check docstring coverage
	@echo "$(BLUE)Checking docstring coverage...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	interrogate $(SRC_DIRS) > $(REPORTS_DIR)/docstring-coverage.txt || true
	interrogate --generate-badge $(REPORTS_DIR)/docstring-coverage.svg $(SRC_DIRS) || true
	@echo "$(GREEN)✅ Docstring coverage analysis completed$(RESET)"

vulnerability-scan: ## Scan for known vulnerabilities
	@echo "$(BLUE)Scanning for known vulnerabilities with safety...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	safety check --json --output $(REPORTS_DIR)/vulnerabilities.json || true
	safety check --output $(REPORTS_DIR)/vulnerabilities.txt || true
	@echo "$(GREEN)✅ Vulnerability scan completed$(RESET)"

# Comprehensive Commands
all-checks: format-check lint type-check security test complexity dead-code docstring-coverage vulnerability-scan ## Run all quality checks
	@echo "$(GREEN)$(BOLD)✅ All quality checks completed!$(RESET)"
	@echo "$(YELLOW)📊 Check the $(REPORTS_DIR)/ directory for detailed reports$(RESET)"

reports: all-checks ## Generate comprehensive reports
	@echo "$(BLUE)Generating comprehensive quality report...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	@echo "# Travel Planner Code Quality Report" > $(REPORTS_DIR)/quality-summary.md
	@echo "Generated on: $$(date)" >> $(REPORTS_DIR)/quality-summary.md
	@echo "" >> $(REPORTS_DIR)/quality-summary.md
	@echo "## Test Coverage" >> $(REPORTS_DIR)/quality-summary.md
	@echo "\`\`\`" >> $(REPORTS_DIR)/quality-summary.md
	@tail -10 $(REPORTS_DIR)/coverage.xml | head -5 >> $(REPORTS_DIR)/quality-summary.md || true
	@echo "\`\`\`" >> $(REPORTS_DIR)/quality-summary.md
	@echo "" >> $(REPORTS_DIR)/quality-summary.md
	@echo "## Security Issues" >> $(REPORTS_DIR)/quality-summary.md
	@echo "\`\`\`" >> $(REPORTS_DIR)/quality-summary.md
	@grep -i "severity" $(REPORTS_DIR)/bandit-report.txt | head -10 >> $(REPORTS_DIR)/quality-summary.md || true
	@echo "\`\`\`" >> $(REPORTS_DIR)/quality-summary.md
	@echo "$(GREEN)✅ Comprehensive reports generated in $(REPORTS_DIR)/$(RESET)"

sonar-scan: ## Run SonarQube analysis
	@echo "$(BLUE)Running SonarQube analysis...$(RESET)"
	@if [ -f sonar-project.properties ]; then \
		sonar-scanner; \
	else \
		echo "$(YELLOW)⚠️  sonar-project.properties not found. Creating default configuration...$(RESET)"; \
		$(MAKE) create-sonar-config; \
		echo "$(YELLOW)📋 Edit sonar-project.properties with your SonarQube server details$(RESET)"; \
	fi

ci-local: ## Simulate CI pipeline locally
	@echo "$(BLUE)$(BOLD)🚀 Running local CI simulation...$(RESET)"
	@echo "$(BLUE)Step 1: Installing dependencies...$(RESET)"
	@$(MAKE) install
	@echo "$(BLUE)Step 2: Code formatting check...$(RESET)"
	@$(MAKE) format-check
	@echo "$(BLUE)Step 3: Linting...$(RESET)"
	@$(MAKE) lint-strict
	@echo "$(BLUE)Step 4: Type checking...$(RESET)"
	@$(MAKE) type-check-strict
	@echo "$(BLUE)Step 5: Security analysis...$(RESET)"
	@$(MAKE) security-strict
	@echo "$(BLUE)Step 6: Running tests...$(RESET)"
	@$(MAKE) test
	@echo "$(GREEN)$(BOLD)✅ Local CI simulation completed successfully!$(RESET)"

# Utility Commands
clean: ## Clean temporary files and reports
	@echo "$(BLUE)Cleaning temporary files...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf $(REPORTS_DIR) 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf htmlcov 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

create-sonar-config: ## Create default SonarQube configuration
	@echo "$(BLUE)Creating SonarQube configuration...$(RESET)"
	@cat > sonar-project.properties << 'EOF'
# SonarQube Configuration for Travel Planner
sonar.projectKey=travel-planner-mcp
sonar.projectName=Travel Planner MCP Server
sonar.projectVersion=1.0.0

# Source code settings
sonar.sources=core,services,tools,tools_solid,server.py,server_solid.py
sonar.tests=tests
sonar.language=py

# Coverage settings
sonar.python.coverage.reportPaths=reports/coverage.xml
sonar.python.xunit.reportPath=reports/junit.xml

# Analysis settings
sonar.python.pylint.reportPaths=reports/pylint-report.txt
sonar.python.bandit.reportPaths=reports/bandit-report.json

# File encoding
sonar.sourceEncoding=UTF-8

# SonarQube server (update these values)
# sonar.host.url=http://localhost:9000
# sonar.login=your-sonar-token
EOF
	@echo "$(GREEN)✅ SonarQube configuration created$(RESET)"

# Quality Gates
quality-gate: ## Check if code meets quality standards
	@echo "$(BLUE)$(BOLD)🚪 Running Quality Gate checks...$(RESET)"
	@PYLINT_SCORE=$$(pylint $(SRC_DIRS) --score=yes 2>/dev/null | grep "Your code has been rated" | sed 's/.*rated at \([0-9.]*\).*/\1/' || echo "0"); \
	if [ "$$(echo "$$PYLINT_SCORE < 8.0" | bc -l 2>/dev/null || echo 1)" -eq 1 ]; then \
		echo "$(RED)❌ Quality Gate Failed: Pylint score $$PYLINT_SCORE < 8.0$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Quality Gate Passed$(RESET)"

# Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(RESET)"
	@mkdir -p docs/static-analysis
	@echo "# Static Analysis Reports" > docs/static-analysis/README.md
	@echo "This directory contains static analysis reports." >> docs/static-analysis/README.md
	@echo "$(GREEN)✅ Documentation structure created$(RESET)"