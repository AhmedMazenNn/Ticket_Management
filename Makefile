.PHONY: help up down build logs shell-backend shell-db migrate makemigrations \
        createsuperuser collectstatic seed test-backend lint-backend \
        frontend-install lint-frontend test-frontend celery-worker celery-beat

# -----------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

# -----------------------------------------------------------------------
# Docker Compose
# -----------------------------------------------------------------------
up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build / rebuild all images
	docker compose build

logs: ## Tail logs for all services
	docker compose logs -f

logs-backend: ## Tail backend logs
	docker compose logs -f backend

logs-worker: ## Tail Celery worker logs
	docker compose logs -f celery_worker

# -----------------------------------------------------------------------
# Django management
# -----------------------------------------------------------------------
shell-backend: ## Open a Django shell inside the backend container
	docker compose exec backend python manage.py shell

shell-db: ## Open a psql shell
	docker compose exec db psql -U $${DB_USER:-ticket_user} -d $${DB_NAME:-ticket_db}

migrate: ## Apply database migrations
	docker compose exec backend python manage.py migrate

makemigrations: ## Create new migrations
	docker compose exec backend python manage.py makemigrations

createsuperuser: ## Create a Django admin superuser
	docker compose exec backend python manage.py createsuperuser

collectstatic: ## Collect static files
	docker compose exec backend python manage.py collectstatic --noinput

seed: ## Load fixture data into the database
	docker compose exec backend python manage.py loaddata fixtures/initial_data.json

# -----------------------------------------------------------------------
# Backend testing & linting
# -----------------------------------------------------------------------
test-backend: ## Run backend tests with coverage
	docker compose exec backend pytest --cov=apps --cov-report=term-missing

lint-backend: ## Lint & format-check backend with ruff
	cd backend && ruff check . && ruff format --check .

format-backend: ## Auto-format backend with ruff
	cd backend && ruff format .

# -----------------------------------------------------------------------
# Frontend
# -----------------------------------------------------------------------
frontend-install: ## Install frontend dependencies
	cd frontend && npm install

lint-frontend: ## Lint & format-check frontend
	cd frontend && npm run lint

format-frontend: ## Auto-format frontend
	cd frontend && npm run format

test-frontend: ## Run frontend tests
	cd frontend && npm test

# -----------------------------------------------------------------------
# Local dev (without Docker)
# -----------------------------------------------------------------------
dev-backend: ## Run Django dev server locally (needs active venv)
	cd backend && python manage.py runserver

dev-frontend: ## Run SvelteKit dev server locally
	cd frontend && npm run dev

celery-worker: ## Run Celery worker locally
	cd backend && celery -A core worker --loglevel=info

celery-beat: ## Run Celery beat locally
	cd backend && celery -A core beat --loglevel=info
