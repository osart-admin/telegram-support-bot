# Makefile

build-web:
	docker compose build web

build-bot:
	docker compose build bot

up:
	docker compose up -d

migrate:
	docker compose exec web python manage.py makemigrations
	docker compose exec web python manage.py migrate

restart-web:
	docker compose restart web

restart-bot:
	docker compose restart bot

rebuild-all: build-web build-bot up migrate

logs-web:
	docker compose logs -f web

logs-bot:
	docker compose logs -f bot
