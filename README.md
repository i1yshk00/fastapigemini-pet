# 🚀 FastAPI Gemini Service

Асинхронный backend‑сервис на **FastAPI** для работы с **Google Gemini API**.  
В проекте есть JWT‑аутентификация, роли (user/admin), история запросов, логирование через Loguru и миграции Alembic.

---

## ✨ Возможности

* 🔮 Отправка запросов в Google Gemini
* 🔐 JWT‑аутентификация и роли (user/admin)
* 🧾 История запросов пользователя и общий доступ для админа
* ⚡ Асинхронная обработка запросов
* 📂 Логирование в stdout + файлы с ротацией
* 🧪 Тесты на pytest + pytest‑asyncio
* 📘 Автоматическая документация FastAPI (Swagger / ReDoc)

---

## 🗂 Структура проекта

```text
fastapi_gemini/
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_create_users_gemini.py
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── gemini.py
│   │   └── admin.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── user.py
│   │   └── gemini.py
│   ├── repositories/
│   │   ├── user.py
│   │   └── gemini.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── gemini.py
│   ├── services/
│   │   ├── auth.py
│   │   └── gemini_client.py
│   └── main.py
├── scripts/
│   └── create_admin.py
├── logs/
├── tests/
├── alembic.ini
├── pyproject.toml
└── README.md
```

---

## 🧩 Технологии

* Python 3.12
* FastAPI + Uvicorn
* SQLAlchemy (async)
* Alembic
* Google Gemini API (`google-genai`)
* Loguru
* Pytest / pytest‑asyncio
* HTTPX (для тестов)

---

## ⚙️ Установка и запуск

### 1️⃣ Установка зависимостей

```bash
poetry install
poetry shell
```

### 2️⃣ Настройка переменных окружения

Создай `.env` в корне проекта:

```env
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key

# Вариант 1 (рекомендуется) — одной строкой
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_gemini

# Вариант 2 — по частям (если не используешь DATABASE_URL)
DB_USER=postgres
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fastapi_gemini
```

Шаблон смотри в `.env.example`.
Важно: не оборачивай значения в кавычки. Пример: `DB_PORT=5432` (а не `'5432'`).

### 2.1️⃣ Описание переменных окружения

* `GEMINI_API_KEY` — ключ доступа к Google Gemini API (обязателен).
* `JWT_SECRET_KEY` — секрет для подписи JWT (обязателен).
* `DATABASE_URL` — строка подключения к БД (рекомендуется).
* `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` — альтернативная сборка URL.
* `ENVIRONMENT` — окружение (`development` / `production`).
* `DEBUG` — флаг дебага (`true`/`false`).

### 3️⃣ Миграции

```bash
alembic upgrade head
```

Если нужно проверить состояние:

```bash
alembic current
alembic heads
```

Если есть рассинхрон между БД и Alembic:

```bash
alembic stamp base
alembic upgrade head
```

### 4️⃣ Запуск приложения

```bash
uvicorn app.main:app --reload
```

После запуска:
* API: `http://127.0.0.1:8000`
* Swagger: `http://127.0.0.1:8000/docs`

---

## 🐳 Docker

### Сборка образа

```bash
docker build -t fastapi-gemini .
```

Если изменялись зависимости и `poetry.lock` устарел, обнови локально:

```bash
poetry lock --no-update
```

### Запуск контейнера

Вариант с `.env`:

```bash
docker run --rm -p 8000:8000 --env-file .env fastapi-gemini
```

Если используется PostgreSQL в Docker или на хосте, убедись, что `DATABASE_URL`
корректно указывает на доступный хост и порт.

Контейнер содержит healthcheck, который проверяет доступность `/docs`.

---

## 🔐 Авторизация в Swagger

В Swagger UI нажми **Authorize** и вставь:

```
Bearer <YOUR_ACCESS_TOKEN>
```

### Как устроена авторизация

* Логин происходит через `POST /auth/login` с форм‑данными.
* В ответе приходит `access_token`.
* Токен нужно передавать в заголовке `Authorization: Bearer <token>`.
* Просроченный или неверный токен вернёт `401`.
* Недостаточные права вернут `403`.

---

## 📡 API эндпоинты

### Auth

**POST `/auth/register`**  
Регистрация пользователя. Пароль: 8–30 символов.

```json
{
  "email": "user@example.com",
  "password": "StrongP@ssw0rd"
}
```

**POST `/auth/login`**  
Логин, принимает `application/x-www-form-urlencoded`:

```text
username=user@example.com&password=StrongP@ssw0rd
```

Ответ:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "expires_in": 86400
}
```

Типовые ошибки:
* `401` — неверный логин или пароль
* `403` — пользователь деактивирован

---

### Gemini (требует Bearer токен)

**POST `/gemini/requests`**  
Отправка prompt в Gemini.

```json
{
  "prompt": "Hi Gemini!",
  "model_version": "gemini-3-flash-preview"
}
```

**GET `/gemini/requests`**  
История запросов текущего пользователя.

Параметры:
* `limit` — количество записей (1–200)
* `offset` — смещение

Типовые ошибки:
* `401` — нет/невалидный токен
* `403` — пользователь деактивирован
* `4xx/5xx` — ошибки Gemini (детали в `detail`)

---

### Admin (только для админов)

**GET `/admin/users`** — список пользователей  
**GET `/admin/users/{user_id}`** — детали пользователя  
**PATCH `/admin/users/{user_id}/access`** — изменить `is_active` / `is_admin`  
**GET `/admin/gemini/requests`** — все запросы (есть фильтр `user_id`)

Ограничения:
* Админ не может изменять свои же флаги доступа.

---

## 📄 Примеры запросов

Подробные примеры запросов смотри в `api.example`.

---

## 🧾 Логирование

Логи пишутся:
* stdout (для Docker / Uvicorn)
* `logs/app.log`
* `logs/error.log`

---

## 🧪 Тестирование

```bash
pytest -v
```

Тесты используют временную SQLite базу (`aiosqlite`) и не требуют PostgreSQL.

---

## 👑 Создание администратора

```bash
python scripts/create_admin.py --email admin@example.com --password "StrongP@ssw0rd"
```

Скрипт проверяет наличие таблиц и валидирует длину пароля (8–30).

---

## 🛠 Модель данных

**users**
* `id`, `email`, `hashed_password`
* `is_active`, `is_admin`
* `created_at`, `updated_at`, `last_login_at`

**gemini_requests**
* `id`, `request_id`, `user_id`
* `prompt`, `response`, `model_version`
* `created_at`, `updated_at`

---

## ✅ Роли и доступ

* Пользователь видит только свои запросы.
* Администратор видит все запросы и управляет доступом пользователей.

---

## 🗺 Roadmap

* [x] Асинхронная СУБД
* [x] JWT‑аутентификация и роли
* [x] История запросов пользователей
* [ ] Rate limiting
* [ ] Retry + backoff для Gemini
* [ ] Docker / docker-compose
* [ ] CI (GitHub Actions)

---

## 💬 Контакты

**Author: Ilya Zogzin**  
**E-Mail: sav1212121212@bk.ru**
