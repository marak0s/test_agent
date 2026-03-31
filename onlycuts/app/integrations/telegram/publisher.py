from onlycuts.app.integrations.telegram.bot_client import TelegramBotClient


class TelegramPublisher:
    def __init__(self, bot: TelegramBotClient):
        self.bot = bot

    def publish(self, chat_id: int, text: str) -> int | None:
        result = self.bot.send_message(chat_id=chat_id, text=text)
        return result.message_id
