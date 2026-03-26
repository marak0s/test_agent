from onlycuts.app.security.validators import TelegramCallbackPayload


def parse_callback_data(callback_data: str) -> TelegramCallbackPayload:
    action, draft_id, content_item_id = callback_data.split("|", maxsplit=2)
    return TelegramCallbackPayload(action=action, draft_id=draft_id, content_item_id=content_item_id)
