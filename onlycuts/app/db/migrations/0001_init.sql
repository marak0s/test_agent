-- Initial schema for onlycuts.
-- TODO: add topic_sources and metrics_snapshots tables in future migration.
CREATE TABLE IF NOT EXISTS channels (
  id UUID PRIMARY KEY,
  code VARCHAR(64) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  language VARCHAR(16) NOT NULL DEFAULT 'en',
  locale VARCHAR(32) NOT NULL DEFAULT 'en_US',
  approver_telegram_user_id BIGINT NULL,
  approver_telegram_chat_id BIGINT NULL,
  publish_telegram_chat_id BIGINT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS topics (
  id UUID PRIMARY KEY,
  channel_id UUID NOT NULL REFERENCES channels(id),
  title VARCHAR(500) NOT NULL,
  status VARCHAR(32) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS content_items (
  id UUID PRIMARY KEY,
  channel_id UUID NOT NULL REFERENCES channels(id),
  topic_id UUID NOT NULL REFERENCES topics(id),
  goal VARCHAR(255) NOT NULL,
  status VARCHAR(32) NOT NULL,
  current_draft_id UUID NULL
);
CREATE TABLE IF NOT EXISTS drafts (
  id UUID PRIMARY KEY,
  content_item_id UUID NOT NULL REFERENCES content_items(id),
  channel_id UUID NOT NULL REFERENCES channels(id),
  body_text TEXT NOT NULL,
  version INT NOT NULL,
  review_status VARCHAR(32) NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals (
  id UUID PRIMARY KEY,
  draft_id UUID NOT NULL REFERENCES drafts(id),
  actor_telegram_user_id BIGINT NOT NULL,
  action VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL,
  source_type VARCHAR(32) NOT NULL,
  source_id VARCHAR(128) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT uq_approvals_source UNIQUE (source_type, source_id)
);
CREATE TABLE IF NOT EXISTS publications (
  id UUID PRIMARY KEY,
  draft_id UUID NOT NULL REFERENCES drafts(id),
  content_item_id UUID NOT NULL REFERENCES content_items(id),
  channel_id UUID NOT NULL REFERENCES channels(id),
  snapshot_text TEXT NOT NULL,
  status VARCHAR(32) NOT NULL,
  telegram_chat_id BIGINT NULL,
  telegram_message_id BIGINT NULL,
  failure_reason VARCHAR(500) NULL,
  queued_at TIMESTAMPTZ NULL,
  published_at TIMESTAMPTZ NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY,
  job_name VARCHAR(128) NOT NULL,
  status VARCHAR(32) NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS artifacts (
  id UUID PRIMARY KEY,
  kind VARCHAR(64) NOT NULL,
  ref_id VARCHAR(128) NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
