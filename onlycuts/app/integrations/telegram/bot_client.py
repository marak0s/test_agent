from dataclasses import dataclass

import httpx

from onlycuts.app.config.settings import settings


@dataclass
class TelegramMessageResult:
    ok: bool
    message_id: int | None = None


class TelegramBotClient:
    """Minimal Telegram Bot API client for sending messages."""

    def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: dict | None = None,
    ) -> TelegramMessageResult:
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        response = httpx.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json=payload,
            timeout=20.0,
        )
        response.raise_for_status()

        data = response.json()
        if not data.get("ok"):
            return TelegramMessageResult(ok=False, message_id=None)

        result = data.get("result", {})
        return TelegramMessageResult(
            ok=True,
            message_id=result.get("message_id"),
        )