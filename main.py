from fastapi import FastAPI, Request, HTTPException
import requests
import os
import json
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("MAX_TOKEN")
API_BASE = "https://platform-api.max.ru"

WELCOME_TEXT = """Здравствуйте! 👋

Добро пожаловать в ROOMSET.

Здесь вы можете быстро:
• открыть виртуальный шоурум;
• связаться с нами по телефону;
• посмотреть адрес шоурума на карте.

Телефон: +7 (950) 730-72-02
Адрес шоурума: г. Челябинск, ул. Чайковского, 173"""

SHOWROOM_URL = "https://room-set.ru/virtualnyj-shourum/"
PHONE_URL = "tel:+79507307202"
CONTACTS_URL = "https://room-set.ru/kontakty/"  # Запасной вариант, если tel: не работает
MAP_URL = "https://maps.google.com/?cid=3523281962486703769&g_mp=CiVnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLkdldFBsYWNlEAIYASAA&hl=ru-RU&source=embed"


def headers():
    if not TOKEN:
        raise RuntimeError("MAX_TOKEN is missing")
    return {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
    }


def build_keyboard():
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [
                    [
                        {
                            "type": "link",
                            "text": "Виртуальный шоурум",
                            "url": SHOWROOM_URL,
                        }
                    ],
                    [
                        {
                            "type": "link",
                            "text": "Адрес шоурума",
                            "url": MAP_URL,
                        }
                    ]
                ]
            },
        }
    ]


def post_max(url: str, payload: dict):
    try:
        resp = requests.post(url, headers=headers(), json=payload, timeout=20)
        logging.info("MAX %s -> %s %s", url, resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json() if resp.content else {}
    except requests.RequestException as e:
        logging.exception("MAX API request failed: %s", e)
        raise


def send_message(chat_id: int, text: str):
    url = f"{API_BASE}/messages?chat_id={chat_id}"
    payload = {
        "text": text,
        "notify": True,
        "attachments": build_keyboard(),
    }
    return post_max(url, payload)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/webhook")
async def webhook(req: Request):
    if not TOKEN:
        raise HTTPException(status_code=500, detail="MAX_TOKEN is missing")
    try:
        body = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logging.info("INCOMING_UPDATE: %s", json.dumps(body, ensure_ascii=False))
    update_type = body.get("update_type") or body.get("type")

    # Пытаемся вытащить chat_id из всех возможных мест
    def extract_chat_id(b):
        return (
            (b.get("chat") or {}).get("chat_id")
            or b.get("chat_id")
            or ((b.get("message") or {}).get("recipient") or {}).get("chat_id")
            or ((b.get("message") or {}).get("chat") or {}).get("chat_id")
        )

    # События старта бота в МАКС: bot_started / bot_added / chat_member_added
    if update_type in ("bot_started", "bot_added", "chat_member_added", "message_chat_created"):
        chat_id = extract_chat_id(body)
        if chat_id:
            send_message(chat_id, WELCOME_TEXT)
        return {"ok": True}

    if update_type == "message_created":
        message = body.get("message") or {}
        recipient = message.get("recipient") or {}
        chat_id = recipient.get("chat_id")
        text = ((message.get("body") or {}).get("text") or "").strip().lower()

        # Любое первое сообщение пользователя тоже триггерит приветствие,
        # не только /start
        if chat_id:
            if text in ("/start", "/старт") or text:
                send_message(chat_id, WELCOME_TEXT)

    return {"ok": True}
