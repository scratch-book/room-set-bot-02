# РУМСЭТ Welcome Bot для MAX

## Стек
- Python 3.11+
- FastAPI + uvicorn
- requests для HTTP-запросов к MAX API
- Деплой: Railway (Procfile)

## Архитектура
Простой webhook-бот для мессенджера MAX. Один файл `main.py`.

## Endpoints
- `GET /` — статус
- `GET /health` — healthcheck
- `POST /webhook` — приём событий от MAX

## Переменные окружения
- `MAX_TOKEN` — токен бота MAX (обязательно)
- `PORT` — порт сервера (Railway задаёт автоматически)

## Команды
- Запуск: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Установка зависимостей: `pip install -r requirements.txt`

## Соглашения
- Токен НИКОГДА не хранится в коде
- Код максимально простой, без лишних абстракций
- Один сценарий: /start → приветственное сообщение + кнопка-ссылка
