from onlycuts.app.config.settings import settings
from onlycuts.app.integrations.telegram.approval_messages import build_approval_message, inline_keyboard
from onlycuts.app.integrations.telegram.bot_client import TelegramBotClient


class ApprovalDispatchService:
    def __init__(self, bot: TelegramBotClient):
        self.bot = bot

    def dispatch(self, topic_title: str, content_item_id: str, draft_id: str, goal: str, body_text: str, review_summary: str | None = None) -> bool:
        msg = build_approval_message(topic_title, content_item_id, draft_id, goal, body_text, review_summary)
        result = self.bot.send_message(
            chat_id=settings.telegram_approver_chat_id,
            text=msg,
            reply_markup=inline_keyboard(draft_id, content_item_id),
        )
        return result.ok
