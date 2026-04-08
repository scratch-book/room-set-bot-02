from fastapi import FastAPI, Request, HTTPException
import requests
import os
import json
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("MAX_TOKEN")
API_BASE = "https://platform-api.max.ru"

WELCOME_TEXT = """Приветствуем вас в официальном цифровом сервисе компании РУМСЭТ! Мы специализируемся на создании эксклюзивных интерьеров, предлагая широкую палитру премиальных декоративных покрытий (включая коллекции Male, Granola, Seta), высококачественных интерьерных красок, а также комплексные услуги по меблировке и декорированию вашего пространства. Мы обеспечиваем полное сопровождение проекта от концепции до финального монтажа.
Для самостоятельного изучения наших коллекций фактур и ознакомления с галереей реализованных проектов, пожалуйста, посетите наш Виртуальный шоурум, нажав на кнопку ниже."""

SHOWROOM_URL = "https://room-set.ru/virtualnyj-shourum/"


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
                            "text": "Открыть виртуальный шоурум",
                            "url": SHOWROOM_URL,
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

    if update_type == "message_created":
        message = body.get("message") or {}
        recipient = message.get("recipient") or {}
        chat_id = recipient.get("chat_id")
        text = ((message.get("body") or {}).get("text") or "").strip().lower()

        if chat_id and text in ("/start", "/старт"):
            send_message(chat_id, WELCOME_TEXT)

    elif update_type == "bot_started":
        chat_id = (body.get("chat") or {}).get("chat_id")
        if chat_id:
            send_message(chat_id, WELCOME_TEXT)

    return {"ok": True}
