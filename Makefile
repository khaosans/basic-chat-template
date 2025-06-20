# BasicChat - Development Makefile
# Common tasks for development and deployment

.PHONY: help install install-dev clean test test-cov lint format type-check run build dist clean-all

# Default target
help:
	@echo "BasicChat - Development Commands"
	@echo "================================="
	@echo "install      - Install production dependencies"
	@echo "install-dev  - Install development dependencies"
	@echo "clean        - Clean build artifacts"
	@echo "test         - Run tests"
	@echo "test-cov     - Run tests with coverage"
	@echo "lint         - Run linting checks"
	@echo "format       - Format code with black"
	@echo "type-check   - Run type checking with mypy"
	@echo "run          - Run the application"
	@echo "build        - Build the package"
	@echo "dist         - Create distribution"
	@echo "clean-all    - Clean all generated files"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all: clean
	rm -rf chroma_db/
	rm -rf logs/
	rm -rf temp/
	rm -f temp_*.mp3
	rm -f *.log

# Testing
test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing

# Code Quality
lint:
	flake8 src/ tests/
	black --check src/ tests/

format:
	black src/ tests/

type-check:
	mypy src/

# Running
run:
	streamlit run src/core/app.py

# Building
build:
	python -m build

dist: build
	python -m twine check dist/*

# Development workflow
dev-setup: install-dev
	@echo "Setting up development environment..."
	@echo "✅ Development environment ready!"

check-all: lint type-check test
	@echo "✅ All checks passed!"

# Ollama management
ollama-check:
	@echo "Checking Ollama installation..."
	@ollama list || (echo "❌ Ollama not found. Please install from https://ollama.ai" && exit 1)
	@echo "✅ Ollama is installed"

ollama-pull-models:
	@echo "Pulling required Ollama models..."
	ollama pull mistral
	ollama pull nomic-embed-text
	ollama pull llava
	ollama pull codellama
	@echo "✅ All models pulled successfully"

# Database management
db-migrate:
	@echo "Running database migrations..."
	python -c "from src.database.database_migrations import run_migrations; run_migrations()"

db-reset:
	@echo "Resetting database..."
	rm -f chat_sessions.db
	python -c "from src.database.database_migrations import run_migrations; run_migrations()"

# Docker (if needed)
docker-build:
	docker build -t basic-chat .

docker-run:
	docker run -p 8501:8501 basic-chat

# Production deployment
prod-install:
	pip install -e . --no-dev

prod-run:
	streamlit run src/core/app.py --server.port 8501 --server.address 0.0.0.0 