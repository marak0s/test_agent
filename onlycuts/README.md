# onlycuts

Production-minded local-first Python skeleton for a Telegram media pipeline.
Initial channel target: `OnlyAiOps`.

## Purpose

This repo bootstraps a safe, auditable flow:
1. ingest topic ideas,
2. plan content items,
3. generate drafts,
4. dispatch drafts to one Telegram approver,
5. handle approval actions (`post`, `regen`, `shorter`, `stronger`, `reject`, `queue`, `help`),
6. publish approved drafts,
7. persist state transitions, approvals, artifacts, and publication snapshots.

## Architecture

- `app/domain`: enums, entities, invariants, domain errors.
- `app/repositories`: SQLAlchemy data access (parameterized ORM, no raw dynamic SQL).
- `app/services`: workflow logic (ingest/planner/draft/review/approval/publish/analytics).
- `app/jobs`: thin job wrappers + `JobRun` persistence.
- `app/integrations/telegram`: bot client, approval message format, callback parsing, publisher.
- `app/security`: sanitization, callback validation, policy stubs, trust boundaries.
- `app/db`: SQLAlchemy models + initial SQL migration file.
- `app/api`: `GET /health`, `POST /admin/run-job`, `POST /telegram/callback`.

## Setup

```bash
cd onlycuts
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

## Environment variables

See `.env.example` for required values:
- `APP_ENV`, `DATABASE_URL`
- Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_APPROVER_USER_ID`, `TELEGRAM_APPROVER_CHAT_ID`, `TELEGRAM_PUBLISH_CHAT_ID`
- Channel: `DEFAULT_CHANNEL_CODE`
- LLM keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`
- `LOG_LEVEL`

## Database migration

Initial SQL migration: `app/db/migrations/0001_init.sql`.

Apply with your standard Postgres migration process (Alembic wiring is intentionally minimal in v1 and can be expanded).

## Run API

```bash
uvicorn onlycuts.app.main:app --reload
```

## Run scheduler

```bash
python scripts/run_scheduler.py
```

## Manual ingest

```bash
python scripts/manual_ingest.py --channel OnlyAiOps --topic "Idea 1" --topic "Idea 2"
```

## Implemented vs deferred

Implemented in this scaffold:
- Domain statuses and core publish invariants.
- SQLAlchemy models for channels/topics/content_items/drafts/approvals/publications/jobs/artifacts.
- Service stubs with real typed interfaces and artifact persistence.
- Telegram approval message + callback validation primitives.
- Basic tests for domain/publish/auth/callback/repository smoke.

Deferred (explicit TODOs):
- Full provider API integrations for OpenAI/Anthropic/Gemini.
- Full alembic env/revision automation.
- Rich review/policy/compliance checks.
- Queue scheduling and publication retry orchestration.
- `topic_sources` and `metrics_snapshots` tables.
