# План деплоя РУМСЭТ Welcome Bot на Railway

## Краткий план (5 минут)

1. ✅ Убедиться, что код в GitHub
2. ✅ Railway: подключить GitHub репозиторий
3. ✅ Railway: добавить переменную `MAX_TOKEN`
4. ✅ Railway: скопировать публичный URL приложения
5. ✅ MAX API: зарегистрировать webhook
6. ✅ Тестировать в MAX

---

## Подробная инструкция

### Шаг 1. Проверить, что код в GitHub

Убедитесь, что репозиторий синхронизирован с GitHub:

```powershell
cd C:\Scripts\room-set-bot-02
git status
git push
```

Репозиторий должен быть на GitHub в вашем аккаунте.

---

### Шаг 2. Подключить Railway

1. Откройте https://railway.app
2. Нажмите `New Project` → `Deploy from GitHub`
3. Авторизуйтесь и выберите репозиторий `room-set-bot-02`
4. Railway автоматически:
   - Найдёт `Procfile`
   - Установит `requirements.txt`
   - Запустит: `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`

Ждите, пока в логах появится:
```
Application startup complete.
```

---

### Шаг 3. Добавить переменную окружения

1. В Railway откройте проект → вкладка `Variables`
2. Нажмите `+ Add Variable`
3. Заполните:
   - Name: `MAX_TOKEN`
   - Value: `ваш_реальный_токен_MAX` (из MAX платформы)

---

### Шаг 4. Получить публичный URL

1. В Railway откройте проект
2. Откройте приложение (нажмите на его имя)
3. Вверху или в меню `Networking` → `Domains` найдите публичный URL:
   ```
   https://room-set-bot-02-production.up.railway.app
   ```

**Важно:** это должен быть **публичный URL**, а не `room-set-bot-02.railway.internal`

---

### Шаг 5. Зарегистрировать webhook в MAX API

Откройте PowerShell и выполните:

```powershell
$token = "ваш_MAX_TOKEN"

$body = @{
  url = "https://room-set-bot-02-production.up.railway.app/webhook"
  update_types = @("message_created", "bot_started")
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://platform-api.max.ru/subscriptions" `
  -Method POST `
  -Headers @{ "Authorization" = $token; "Content-Type" = "application/json" } `
  -Body $body
```

Должен вернуть: `{"ok": true}`

---

### Шаг 6. Тестировать

1. Откройте MAX мессенджер
2. Найдите вашего бота (ник типа `id772206988783_1_bot`)
3. Напишите: `/start` или `/старт`
4. **Бот должен ответить приветственным сообщением с кнопкой**

Если не работает → проверьте логи Railway (см. секцию `Troubleshooting` ниже).

---

## Проверки

### Проверить, что webhook зарегистрирован правильно

```powershell
$token = "ваш_MAX_TOKEN"

Invoke-RestMethod -Uri "https://platform-api.max.ru/subscriptions" `
  -Method GET `
  -Headers @{ "Authorization" = $token } | ConvertTo-Json -Depth 5
```

Должен показать ваш публичный URL.

### Проверить, что сервер доступен

```powershell
curl.exe https://room-set-bot-02-production.up.railway.app/
curl.exe https://room-set-bot-02-production.up.railway.app/health
```

Должны вернуть JSON:
```json
{"status":"ok"}
{"ok":true}
```

---

## Troubleshooting

### Проблема: Логов нет в Railway

**Решение:**
1. Убедитесь, что вы смотрите свежие логи (перезагрузите вкладку)
2. Проверьте, что webhook зарегистрирован на **публичный URL** (не `.railway.internal`)
3. Проверьте, что `MAX_TOKEN` задан в переменных Railway

### Проблема: Бот не отвечает, но логи есть

**Проверяйте в логах:**
```
ERROR:root:MAX API request failed: ...
```

Это значит:
- Токен неправильный
- API MAX недоступна (редко)
- Синтаксис запроса неверный

**Решение:** Проверьте `MAX_TOKEN` в коде и в Railway.

### Проблема: `400 Bad Request` на `/webhook`

**Решение:** MAX отправляет неверный JSON. Обновите webhook с правильными `update_types`:

```powershell
$token = "ваш_MAX_TOKEN"

$body = @{
  url = "https://room-set-bot-02-production.up.railway.app/webhook"
  update_types = @("message_created", "bot_started")
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://platform-api.max.ru/subscriptions" `
  -Method POST `
  -Headers @{ "Authorization" = $token; "Content-Type" = "application/json" } `
  -Body $body
```

---

## Чек-лист перед production

- [ ] Код в GitHub синхронизирован
- [ ] Railway проект создан и запущен
- [ ] `MAX_TOKEN` добавлен в Variables
- [ ] Webhook зарегистрирован на **публичный URL**
- [ ] Webhook включает `message_created` и `bot_started`
- [ ] Тестовое сообщение `/start` получает ответ в MAX
- [ ] Логи Railway показывают `INCOMING_UPDATE`

---

## Быстрая пересборка (если код изменился)

Если вы изменили `main.py`:

1. **Закоммитьте и запушьте в GitHub:**
   ```powershell
   git add main.py
   git commit -m "Fix: описание изменения"
   git push
   ```

2. **Railway автоматически пересоберёт** приложение (смотрите Deploy Logs)

3. **Тестируйте в MAX**

Никаких ручных действий в Railway не требуется — всё работает автоматически.

---

## Полезные ссылки

- [MAX API документация](https://dev.max.ru/docs-api)
- [MAX Webhook docs](https://dev.max.ru/docs/chatbots/bots-coding/prepare#настраиваем-уведомления)
- [Railway документация](https://docs.railway.app)
