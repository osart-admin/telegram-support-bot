docker system prune -af --volumes
docker compose build bot
docker compose up -d bot
docker system prune -af --volumes
docker compose build web
docker compose up -d web
docker system prune -af --volumes
