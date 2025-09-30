# CRM сервис

Архитектура (слои):

1. domain — бизнес-модели / правила (чистые структуры, без IO).
2. application (interactors / use-cases) — координация бизнес-операций, транзакции, вызов репозиториев и брокера.
3. infrastructure — реализации: репозитории (SQLAlchemy), брокер (RabbitMQ aio-pika), провайдер времени, идемпотентность.
4. presentation — FastAPI хендлеры (DTO <-> domain).
5. messaging (entrypoints.consumer) — подписка на очереди, диспетчеризация сообщений -> interactors.
6. entrypoints.api — запуск HTTP.
7. config — pydantic Settings.

Data flow HTTP:
Client -> FastAPI Handler -> Interactor -> Repository (Postgres) / Publisher -> Response DTO.

Data flow Messaging:
RabbitMQ message -> Consumer -> Interactor -> Repository / EventOut -> (publish).

Тестовые уровни:

- unit: изолированно (моки).
- integration: interactors + реальный Postgres (в docker / testcontainers) + временные таблицы.
- e2e: поднятый FastAPI (TestClient/httpx) + миграции + фейковый брокер (или реальный контейнер).

## Быстрый старт (локально)

Poetry:

```
poetry install
poetry shell
cp .env.example .env
alembic upgrade head
uvicorn crm.entrypoints.api:app --reload
```

Docker (все сервисы):

```
docker compose up --build
```

Проверка API:

```
curl http://localhost:8000/health
```

## Тесты

Интеграционные:

```
pytest -m "integration" -q
```

E2E:

```
pytest -m "e2e" -q
```

Все + покрытие:

```
pytest --cov=crm --cov-report=term-missing
```

## Переменные окружения (пример)

- DATABASE_URL=postgresql+asyncpg://crm:crm@localhost:5432/crm
- RABBITMQ_URL=amqp://guest:guest@localhost:5672//
- APP_MODE=api|worker

## Миграции

```
alembic revision -m "init"
alembic upgrade head
```

## TODO

- Заполнить реальные interactors в crm/application/interactors.
- Описать domain-модели.
- Добавить схемы request/response.
- Актуализировать тесты (заменить TODO / фейковые имена модулей).

## Лицензия

Proprietary / internal (измените при необходимости).
