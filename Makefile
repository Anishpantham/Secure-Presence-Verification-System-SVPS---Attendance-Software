.PHONY: setup db migrate seed api dashboard test build stop
setup:
	python3 scripts/init_env.py
	uv sync --project backend --frozen
	python3 scripts/download_models.py
	cd dashboard && npm ci
	cd mobile && npm ci
db:
	docker compose up -d db --wait
migrate:
	bash scripts/backend.sh alembic upgrade head
seed:
	bash scripts/backend.sh python -m app.seed
api:
	bash scripts/backend.sh uvicorn app.main:app --host 0.0.0.0 --port 8000
dashboard:
	cd dashboard && npm run dev -- --host 0.0.0.0
test:
	bash scripts/backend.sh pytest
	cd dashboard && npm test -- --run
	cd mobile && npm test -- --run
build:
	cd dashboard && npm run build
	cd mobile && npm run typecheck
stop:
	docker compose stop
