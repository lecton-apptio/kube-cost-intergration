.PHONY: help install test lint format type-check clean all

help:
	@echo "Available commands:"
	@echo "  make install      - Install package with dev dependencies"
	@echo "  make test         - Run tests with coverage"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code with Black"
	@echo "  make type-check   - Run type checking with MyPy"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make all          - Run all checks (format, lint, type-check, test)"

install:
	pip install -e ".[dev]"

test:
	pytest --cov=kubecost_integration --cov-report=term-missing --cov-report=xml

lint:
	ruff check kubecost_integration tests

lint-fix:
	ruff check --fix kubecost_integration tests

format:
	black kubecost_integration tests

format-check:
	black --check kubecost_integration tests

type-check:
	mypy kubecost_integration

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

all: format lint type-check test
	@echo "✅ All checks passed!"

# Made with Bob
