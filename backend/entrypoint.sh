#!/bin/bash

echo "Ожидание готовности Postgres..."
until nc -z db 5432; do
    sleep 1
done
echo "Postgres готов. Выполнение миграций..."
alembic upgrade head

python app/seed.py
echo "Запуск сервера..."
exec gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
