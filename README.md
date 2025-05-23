# 🤖 Telegram Support Bot

AI-бот службы поддержки с голосовыми сообщениями, умным поиском по FAQ, fallback-ответами от GPT4All или ChatGPT и веб-админкой на Django.

## 📦 Функции

- 🎙️ Распознавание голосовых сообщений (Whisper)
- 📚 Поиск по FAQ на основе смысловых векторов (Sentence Transformers)
- 💬 Fallback ответы через:
  - GPT4All (локально)
  - ChatGPT (через OpenAI API)
- 🧾 Логирование сообщений в базу
- 🛠️ Django-админка:
  - Просмотр и ответ по обращениям
  - Добавление/редактирование FAQ
  - Кнопка «📌 Зберегти в FAQ» для ответа администратора
- ✅ Кнопки «Допомогло / Не допомогло» для пользователей
- 🔁 Автоматическое обновление индекса FAQ при изменении

## 🧱 Архитектура

![Архитектура](support_bot_architecture.png)

## 🚀 Развёртывание

```bash
git clone https://github.com/osart-admin/telegram-support-bot.git
cd telegram-support-bot

cp .env.example .env  # настрой переменные
docker compose up --build

telegram-support-bot/
├── bot/                 # Telegram bot (Aiogram)
│   ├── bot.py
│   ├── db_logger.py
│   ├── fallback_chain.py
│   ├── transcribe.py
│   └── embeddings/      # build_index.py
├── web/                 # Django admin
│   └── supportapp/
│       ├── models.py
│       ├── admin.py
│       ├── handlers.py
│       └── templates/admin/...
├── db/                  # faq_index.pkl
├── audio/               # Голосовые сообщения
├── models/              # GPT4All .gguf
└── docker-compose.yml

⚠️ Примечание
	•	GPT4All работает локально через .gguf-файл (Mistral).
	•	Поддерживается fallback через openai.ChatCompletion.

🤖 Bot (Telegram-бот)

🧱 Технологии и библиотеки:
	•	Python 3.10
	•	Aiogram 3 — асинхронный Telegram Bot Framework
	•	aiohttp — асинхронные HTTP-запросы (для загрузки голосовых сообщений)
	•	gpt4all — локальная LLM (например, Mistral gguf)
	•	openai — fallback к ChatGPT через API
	•	whisper / transcribe_audio — распознавание голосовых сообщений в текст
	•	sentence-transformers — векторизация текста для FAQ-поиска
	•	scikit-learn — cosine_similarity для нахождения ближайшего ответа
	•	MySQLdb — логирование обращений и сообщений в базу (через db_logger.py)
	•	Docker — изолированная сборка и запуск контейнера

🔧 Функциональность:
	•	Обрабатывает голосовые и текстовые сообщения
	•	Сначала ищет ответ в FAQ (векторный поиск)
	•	Если не найдено — вызывает GPT4All (локально), и если не сработало — обращается к ChatGPT
	•	Логирует все запросы/ответы в базу
	•	Отправляет кнопки ✅ Допомогло / ❌ Не допомогло
	•	Реализует callback_query-обработчики

⸻

🌐 Web (админка и база знаний)

🧱 Технологии и библиотеки:
	•	Django 5.2.1
	•	Python 3.10
	•	Django Admin — удобная панель управления
	•	MySQL (через mysqlclient)
	•	Whitenoise — подача статики
	•	python-dotenv — переменные окружения
	•	telegram (python-telegram-bot==13.15) — для отправки сообщений в Telegram
	•	sentence-transformers — пересборка FAQ-индекса после изменений
	•	huggingface_hub[hf_xet] — ускорение загрузки моделей

🔧 Функциональность:
	•	Управление FAQ, обращениями и сообщениями через Django Admin
	•	Отправка сообщений администратора в Telegram (однократно, без дублей)
	•	Кнопка 📌 Зберегти в FAQ в админке
	•	Автоматическая пересборка faq_index.pkl при изменении FAQ
	•	Сигналы Django (post_save) для логики автоматизации

⸻

🐳 Инфраструктура
	•	Docker Compose управляет 3 сервисами:
	•	bot — контейнер с Telegram-ботом
	•	web — контейнер с Django
	•	mysql — БД MySQL 8.0
	•	volume ./db:/app/db — хранение FAQ-индекса
	•	volume ./audio:/app/audio — временные голосовые файлы
	•	volume /opt/models:/models — gguf-модели для GPT4All
