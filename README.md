# Payment API - REST API Backend

Асинхронное веб-приложение для управления платежами, счетами и пользователями.

## Стек технологий

- Python 3.14+
- Sanic (веб-фреймворк)
- SQLAlchemy (ORM)
- PostgreSQL (база данных)
- Docker Compose
- Poetry (управление зависимостями)

## Запуск проекта

### Вариант 1: С использованием Docker Compose

1. Убедитесь, что Docker и Docker Compose установлены в вашей системе.

2. Клонируйте репозиторий и перейдите в директорию проекта:
```bash
git clone <repository-url>
cd python-test-job
```

3. Запустите Docker Compose:
```bash
docker-compose up -d
```

4. Примените миграции:
```bash
docker-compose exec app alembic upgrade head
```

5. Приложение будет доступно по адресу: `http://localhost:8000`

### Вариант 2: Без Docker

1. Убедитесь, что Python 3.14+, PostgreSQL и [Poetry](https://python-poetry.org/) установлены.

2. Создайте базу данных:
```sql
CREATE DATABASE payment_db;
```

3. Установите зависимости через Poetry:
```bash
poetry install
```

4. Скопируйте файл `.env.example` в `.env` и настройте переменные окружения:
```bash
cp .env.example .env
```

5. Примените миграции:
```bash
poetry run alembic upgrade head
```

6. Запустите приложение:
```bash
poetry run python -m app.main
```

7. Приложение будет доступно по адресу: `http://localhost:8000`

## Тестовые аккаунты

### Пользователь
- **Email:** user@example.com
- **Пароль:** password123

### Администратор
- **Email:** admin@example.com
- **Пароль:** admin123

## API Эндпоинты

### Аутентификация

| Метод | Описание | URL |
|-------|----------|-----|
| POST | Авторизация пользователя | `/api/auth/login` |
| POST | Авторизация администратора | `/api/auth/admin/login` |

### Пользователь

| Метод | Описание | URL | Авторизация |
|-------|----------|-----|-------------|
| GET | Данные о себе | `/api/user/me` | Bearer Token |
| GET | Список счетов | `/api/user/accounts` | Bearer Token |
| GET | Список платежей | `/api/user/payments` | Bearer Token |

### Администратор

| Метод | Описание | URL | Авторизация |
|-------|----------|-----|-------------|
| GET | Данные о себе | `/api/admin/me` | Bearer Token |
| GET | Список пользователей | `/api/admin/users` | Bearer Token |
| POST | Создать пользователя | `/api/admin/users` | Bearer Token |
| PUT | Обновить пользователя | `/api/admin/users/<user_id>` | Bearer Token |
| DELETE | Удалить пользователя | `/api/admin/users/<user_id>` | Bearer Token |

### Вебхук платежей

| Метод | Описание | URL | Авторизация |
|-------|----------|-----|-------------|
| POST | Обработка вебхука | `/api/webhook/payment` | Нет |

## Примеры запросов

### Авторизация пользователя
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Получение данных о себе
```bash
curl -X GET http://localhost:8000/api/user/me \
  -H "Authorization: Bearer <token>"
```

### Вебхук платежа
```bash
curl -X POST http://localhost:8000/api/webhook/payment \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
  }'
```

## Структура проекта

```
python-test-job/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── admin.py
│   │   ├── account.py
│   │   └── payment.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── account.py
│   │   └── payment.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── admin.py
│   │   └── payment.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── admin.py
│   │   └── webhook.py
│   └── middleware/
│       ├── __init__.py
│       └── auth.py
├── migrations/
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── poetry.lock
├── alembic.ini
├── .env
└── .env.example
```"# python-test-job" 
