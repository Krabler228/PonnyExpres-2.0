# PonnyExpres 2.0

Сервис регистрации и отслеживания посылок.  
Стек: FastAPI, PostgreSQL, Redis, Celery (worker + beat), Docker Compose.  
Пользователи идентифицируются по cookie `session_id` (без авторизации).

## Требования
- Компик
- Docker Desktop (или Docker Engine) + Docker Compose v2. [web:171]
- Git.
- Для удобства работы с бд можно DBeaver а можно и без него как вам удобнее бога ради
- только постгрес поставь(на английском языке)

## Конфигурация

1) Создать файл `.env` рядом с `docker-compose.yml`:

cp .env.example .env

text

2) Заполнить значения в `.env` (пароли и т.п.).

Важно: `TEST_DATABASE_URL` используется при запуске тестов локально. Если тесты запускать внутри Docker, `localhost` работать не будет — нужно будет указывать имя сервиса в Docker-сети. [web:110][web:109]

## Запуск проекта

Поднять все сервисы:

docker compose up --build

text

Запуск в фоне:

docker compose up -d --build

text

Проверить, что сервисы поднялись:

docker compose ps

text

Посмотреть логи приложения:

docker compose logs -f app

text

Остановить и удалить контейнеры:

docker compose down

text

## Документация API (Swagger)

После запуска сервиса документация доступна по адресам:  
- Swagger UI: http://localhost:8000/docs [web:178]  
- ReDoc: http://localhost:8000/redoc [web:178]

Healthcheck:
- http://localhost:8000/health

## Как работать с сервисом

### Сессии

Авторизации нет. При первом запросе сервис создаёт cookie `session_id`.  
Все операции со списком посылок выполняются в рамках текущей сессии (то есть “мои посылки” зависят от cookie).

Если вы тестируете через curl и хотите сохранять сессию между запросами, используйте cookie-jar:

Создать сессию
curl -c cookies.txt http://localhost:8000/health

Дальше использовать ту же сессию
curl -b cookies.txt http://localhost:8000/parcels/types

text

### Типы посылок

Получить список типов:

curl -b cookies.txt http://localhost:8000/parcels/types

text

### Регистрация посылки

curl -b cookies.txt -X POST http://localhost:8000/parcels
-H "Content-Type: application/json"
-d '{
"name": "Phone",
"weight": 1.2,
"parcel_type_id": 2,
"declared_value_usd": 800
}'

text

В ответ вернётся созданная посылка (включая `id` и `tracking_code`).

### Получить список своих посылок

curl -b cookies.txt "http://localhost:8000/parcels?page=1&page_size=20"

text

Фильтры:
- `parcel_type_id` — фильтрация по типу
- `has_delivery_cost=true|false` — фильтр по наличию рассчитанной стоимости

Пример:

curl -b cookies.txt "http://localhost:8000/parcels?page=1&page_size=20&parcel_type_id=2&has_delivery_cost=false"

text

### Получить посылку по id (только в рамках своей сессии)

curl -b cookies.txt http://localhost:8000/parcels/1

text

Если `id` принадлежит другой сессии или не существует — будет 404.

### Публичный трекинг по tracking_code

После создания посылки у неё есть `tracking_code`. Публичный роут позволяет получить информацию по нему:

curl http://localhost:8000/public/parcels/TRACKING_CODE_HERE

text

Если стоимость доставки ещё не рассчитана, в ответе возвращается текст “Цена не рассчитана”.

## Фоновый расчёт стоимости доставки

Стоимость доставки пересчитывается периодически (Celery Beat) каждые 5 минут. [web:45]  
Задача выбирает посылки с `delivery_cost_rub IS NULL` и выставляет стоимость по формуле:

`delivery_cost_rub = (weight * 0.5 + declared_value_usd * 0.01) * usd_rate`

Курс USD/RUB берётся из `https://www.cbr-xml-daily.ru/daily_json.js` и кэшируется в Redis (ключ `usd_rate`, TTL около 5 минут).

### Ручной запуск пересчёта (для отладки)

curl -X POST http://localhost:8000/debug/recalculate_delivery

text

В ответ вернётся `task_id` Celery-задачи.

## Запуск тестов

Локально (вне Docker):

pytest

text

С покрытием:

pytest --cov=src/app --cov-report=term-missing

text

## Сервисы в docker-compose

- `app` — FastAPI приложение (uvicorn)
- `postgres` — PostgreSQL
- `redis` — Redis
- `celery_worker` — обработчик задач Celery
- `celery_beat` — планировщик периодических задач Celery