from dataclasses import dataclass

import httpx

from onlycuts.app.config.settings import settings


@dataclass
class TelegramMessageResult:
    ok: bool
    message_id: int | None = None
    error: str | None = None


class TelegramBotClient:
    """Telegram Bot API client using HTTP transport.

    Keeps interface small for easy mocking in tests.
    """

    def __init__(self, token: str | None = None):
        self.token = token or settings.telegram_bot_token

    def send_message(self, chat_id: int, text: str, reply_markup: dict | None = None) -> TelegramMessageResult:
        if not self.token:
            return TelegramMessageResult(ok=False, error="TELEGRAM_BOT_TOKEN is not configured")

        payload: dict = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            response = httpx.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            body = response.json()
        except Exception as exc:  # pragma: no cover - integration boundary
            return TelegramMessageResult(ok=False, error=str(exc))

        if not body.get("ok"):
            return TelegramMessageResult(ok=False, error=str(body))

        return TelegramMessageResult(ok=True, message_id=body.get("result", {}).get("message_id"))
