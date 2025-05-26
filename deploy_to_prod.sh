#!/bin/bash

# ==== Настройки ====
PROD_USER=deployer
PROD_HOST=10.1.0.95
PROD_DIR=/opt/telegram-support-bot
SSH_KEY=~/.ssh/prod_deploy
MYSQL_USER=root              # <--- Замени на своё!
MYSQL_PASS=your_mysql_password  # <--- Замени на своё!
MYSQL_DB=support             # <--- Название БД

# ==== Синхронизируем файлы ====
rsync -az --delete \
  --exclude-from='.deployignore' \
  -e "ssh -i $SSH_KEY" \
  ./ $PROD_USER@$PROD_HOST:$PROD_DIR

# ==== Деплой и миграции ====
ssh -i $SSH_KEY $PROD_USER@$PROD_HOST "
  docker system prune -af --volumes
  docker system prune -af
  cd $PROD_DIR &&
  docker-compose pull &&
  docker-compose up -d --build &&
  sleep 5 &&
  docker-compose exec -T web python3 manage.py migrate
"

# ==== Ручная подстраховка по MySQL (на всякий случай) ====
ssh -i $SSH_KEY $PROD_USER@$PROD_HOST "
  docker-compose exec -T mysql mysql -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_DB -e \"
  ALTER TABLE supportapp_messagethread
    ADD COLUMN IF NOT EXISTS first_name varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS last_name varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS username varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS photo_url varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS last_message_at datetime NULL;
  \" || true
"

echo "Деплой завершен!"
