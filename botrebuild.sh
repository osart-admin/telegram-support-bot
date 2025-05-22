docker system prune -af --volumes
docker compose build bot
docker compose up -d bot
docker compose logs -f bot
