docker system prune -af --volumes
docker compose build web
docker compose up -d web
docker compose logs -f web
