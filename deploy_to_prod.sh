#!/bin/bash

# ==== Настройки ====
PROD_USER=deployer
PROD_HOST=10.1.0.95
PROD_DIR=/opt/telegram-support-bot
SSH_KEY=~/.ssh/prod_deploy

# ==== Синхронизируем файлы ====
rsync -az --delete \
  --exclude-from='.deployignore' \
  -e "ssh -i $SSH_KEY" \
  ./ $PROD_USER@$PROD_HOST:$PROD_DIR

# ==== Очистка Docker перед обновлением, деплой, повторная очистка ====
ssh -i $SSH_KEY $PROD_USER@$PROD_HOST "
  docker system prune -af --volumes
  cd $PROD_DIR &&
  docker compose pull &&
  docker compose up -d --build
  docker system prune -af --volumes
"

echo "Деплой завершен!"
