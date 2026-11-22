.PHONY: up down run-module-1

up:
	docker compose up -d

down:
	docker compose down

run-module-1:
	cd modules/01-backend-core && uvicorn app.main:app --reload --port 8000