.PHONY: help install dev build test clean docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

dev: ## Start development servers
	@echo "Starting development environment..."
	docker-compose -f docker/docker-compose.yml up --build

build: ## Build for production
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Building backend..."
	cd backend && python -m build

test: ## Run all tests
	@echo "Running frontend tests..."
	cd frontend && npm test
	@echo "Running backend tests..."
	cd backend && python -m pytest

clean: ## Clean build artifacts
	@echo "Cleaning frontend..."
	cd frontend && rm -rf dist node_modules
	@echo "Cleaning backend..."
	cd backend && rm -rf build dist *.egg-info __pycache__

docker-build: ## Build Docker images
	docker-compose -f docker/docker-compose.yml build

docker-up: ## Start Docker containers
	docker-compose -f docker/docker-compose.yml up -d

docker-down: ## Stop Docker containers
	docker-compose -f docker/docker-compose.yml down

docker-logs: ## View Docker logs
	docker-compose -f docker/docker-compose.yml logs -f