# Sales Aggregator API

Мини-сервис для загрузки, хранения и анализа данных о продажах с маркетплейсов.

## Реализованная функциональность

- Загрузка продаж через API и CSV
- Агрегация метрик (выручка, прибыль, маржинальность и др.)
- Группировка по маркетплейсу, дате и статусу 
- Топ товаров по выручке / количеству / прибыли 
- Конвертация метрик в USD (с кэшированием курса)
- Фильтрация и пагинация данных

===

## Архитектура

Проект разделён на слои:

- `models` — Pydantic-модели
- `routers` — API эндпоинты
- `services` — бизнес-логика (агрегация, хранение, валюта)

Хранение реализовано in-memory (можно заменить на БД).

===

## Запуск

### Вариант 1 — локально

```bash
cd sales_aggregator
pip install -r requirements.txt
uvicorn main:app 
```

Сервис будет доступен:
http://localhost:8000

Swagger UI:
http://localhost:8000/docs

===

### Вариант 2 — через Docker

Сборка и запуск из корня:

```bash
docker-compose up --build -d
```

После запуска:
http://localhost:8000
http://localhost:8000/docs

===

## Основные эндпоинты

### Продажи

- `POST /sales` — добавить продажи (batch)
- `GET /sales` — получить список с фильтрацией

===

### Аналитика

- `GET /analytics/summary` — агрегированные метрики
- `GET /analytics/summary-usd` — метрики в USD
- `GET /analytics/top-products` — топ товаров
- `POST /analytics/upload-csv` — загрузка CSV

===

## Пример данных

```json
{
  "order_id": "ORD-001",
  "marketplace": "ozon",
  "product_name": "Кабель USB-C",
  "quantity": 3,
  "price": 450.0,
  "cost_price": 120.0,
  "status": "delivered",
  "sold_at": "2025-03-15"
}
```

===

## Валидация

- `marketplace` — ozon / wildberries / yandex_market
- `price`, `cost_price` > 0
- `quantity` ≥ 1
- `sold_at` <= now()

===

## CSV загрузка

- Поддерживается загрузка через `/analytics/upload-csv`
- Ошибки возвращаются с номерами строк 
- Частично валидные данные сохраняются

===

## Особенности реализации

- Агрегации выполнены через Pandas 
- Курс валют кэшируется на 1 час 
- Архитектура позволяет быстро подключить БД

===

## Возможные улучшения

- Подключение SQLite / PostgreSQL (с доработкой моделей) 
- Добавление тестов (pytest)
- Логирование (JSON)
