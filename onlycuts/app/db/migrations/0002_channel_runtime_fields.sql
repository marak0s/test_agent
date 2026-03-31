-- Adds channel-specific runtime routing fields.
ALTER TABLE channels ADD COLUMN IF NOT EXISTS language VARCHAR(16) NOT NULL DEFAULT 'en';
ALTER TABLE channels ADD COLUMN IF NOT EXISTS locale VARCHAR(32) NOT NULL DEFAULT 'en_US';
ALTER TABLE channels ADD COLUMN IF NOT EXISTS approver_telegram_user_id BIGINT NULL;
ALTER TABLE channels ADD COLUMN IF NOT EXISTS approver_telegram_chat_id BIGINT NULL;
ALTER TABLE channels ADD COLUMN IF NOT EXISTS publish_telegram_chat_id BIGINT NULL;
ALTER TABLE channels ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
