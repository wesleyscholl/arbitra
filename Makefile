.PHONY: help install test test-risk test-coverage clean setup-podman setup-local start-podman stop-podman

help: ## Show this help message
	@echo "Arbitra - AI Crypto Trading Agent"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "For detailed installation options, see INSTALLATION.md"

install: ## Install Python dependencies
	pip install -r requirements.txt
	pip install -e .

test: ## Run all tests
	pytest tests/ -v

test-risk: ## Run risk module tests only
	pytest tests/risk/ -v --cov=src/risk

test-coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "Coverage report: htmlcov/index.html"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	ptw tests/risk/ -- -v

clean: ## Clean up generated files
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Podman commands
setup-podman: ## Install podman and podman-compose (macOS)
	brew install podman podman-compose
	podman machine init --cpus 2 --memory 4096
	podman machine start

start-podman: ## Start services with podman-compose
	podman-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@podman-compose ps

stop-podman: ## Stop podman services
	podman-compose down

logs-podman: ## View podman service logs
	podman-compose logs -f

# Local installation commands (macOS)
setup-local: ## Install PostgreSQL and Redis locally (macOS)
	brew install postgresql@15 redis
	brew services start postgresql@15
	brew services start redis
	createdb arbitra || true
	@echo "Local services started"

stop-local: ## Stop local services (macOS)
	brew services stop postgresql@15
	brew services stop redis

# Development commands
format: ## Format code with black
	black src/ tests/

lint: ## Lint code with flake8
	flake8 src/ tests/ --max-line-length=100

type-check: ## Type check with mypy
	mypy src/

check: format lint type-check test ## Run all checks (format, lint, type-check, test)

# Quick start commands
quick-start: install test-risk ## Quick start - install and test
	@echo ""
	@echo "✓ Setup complete! Risk module tests passed."
	@echo ""
	@echo "Next steps:"
	@echo "  1. Review test results above"
	@echo "  2. Check QUICKSTART.md for usage examples"
	@echo "  3. Run 'make test-coverage' to see coverage report"

dev-setup: install start-podman test ## Full dev setup with Podman
	@echo ""
	@echo "✓ Development environment ready!"

# Docker compatibility (for users who still have it)
docker-start: ## Start services with docker-compose
	docker-compose -f podman-compose.yml up -d

docker-stop: ## Stop docker services
	docker-compose -f podman-compose.yml down
