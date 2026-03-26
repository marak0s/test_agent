from dataclasses import dataclass


@dataclass
class TelegramMessageResult:
    ok: bool
    message_id: int | None = None


class TelegramBotClient:
    """Thin wrapper; returns mockable results for tests."""

    def send_message(self, chat_id: int, text: str, reply_markup: dict | None = None) -> TelegramMessageResult:
        # TODO integrate python-telegram-bot async client.
        return TelegramMessageResult(ok=True, message_id=1)
