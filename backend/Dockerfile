# Используем официальный образ Python
FROM python:3.11

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y netcat-openbsd

RUN mkdir /messanger

# Устанавливаем рабочую директорию
WORKDIR /messanger

# Копируем requirements.txt и устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Копируем и делаем исполняемым скрипт запуска
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Запускаем приложение
CMD ["/entrypoint.sh"]
# CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8080"]
