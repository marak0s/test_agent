# onlycuts

Production-minded local-first Python service for the OnlyCuts Telegram pipeline. Current MVP channel: `OnlyAiOps`.

## What is implemented now

- Layered architecture: domain, repositories, services, integrations, jobs, API.
- Topic ingest -> planning -> draft generation -> review -> approval -> publish skeleton.
- Telegram approval loop with **inline callbacks** and **reply commands** routed through the same approval service gate.
- Single approver enforcement (`TELEGRAM_APPROVER_USER_ID` + `TELEGRAM_APPROVER_CHAT_ID`).
- Idempotent action handling by source event (`callback_query.id` / derived reply source id).
- Publish path with explicit queue vs publish-now flow and immutable text snapshot persistence.
- SQLAlchemy models + SQL migration targeting **Postgres runtime**.

## Safety model

1. External text is data only, never executable instructions.
2. LLM output is proposal material, never truth.
3. No dynamic SQL formatting; ORM/parameterized access only.
4. No shell/tool execution from content text.
5. Approval actor and callback payload are validated.
6. Publishing requires explicit approval and invariant checks.
7. Publication payload snapshot is immutable once recorded.
8. Audit trail kept in approvals/artifacts/publications.

## What is still TODO

- Real Telegram Bot API transport wiring (currently adapter is intentionally lightweight).
- Real LLM provider calls and stronger factuality/policy checks.
- Natural language queue scheduling resolution (`queue tomorrow 10:00` currently stored as note).
- Retry/backoff strategies and richer analytics snapshots.
- Full cron scheduling of the full operator cycle job (currently manual trigger/script).
- Automatic RU<->EN fan-out/translation is not implemented yet.
- Alembic runtime env/revision flow (schema SQL file already present).


## Multi-channel readiness (RU/EN)

Channels now carry runtime routing fields in DB so each channel can define its own Telegram and language settings:
- `language`, `locale`
- `approver_telegram_user_id`, `approver_telegram_chat_id`
- `publish_telegram_chat_id`
- `is_active`

Routing behavior:
- Approval dispatch uses channel approver chat when present.
- Approval authorization checks channel approver user/chat when present.
- Publish uses channel publish chat when present.
- Global env vars remain compatibility defaults when channel fields are null.

## Environment variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL` (Postgres, default `postgresql+psycopg://postgres:postgres@localhost:5432/onlycuts`)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_APPROVER_USER_ID`
- `TELEGRAM_APPROVER_CHAT_ID`
- `TELEGRAM_PUBLISH_CHAT_ID`
- `DEFAULT_CHANNEL_CODE`
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`
- `APP_ENV`, `LOG_LEVEL`

## API endpoints

- `GET /health`
- `POST /admin/run-job`
- `POST /telegram/callback`

`POST /telegram/callback` accepts either:
- callback payload (flat `callback_data` + actor ids, or nested `callback_query`) for inline button actions, or
- message payload (`message`) for reply commands.

## Approver commands

Supported actions:
- `post`
- `regen`
- `regen stronger`
- `shorter`
- `stronger`
- `reject`
- `queue`
- `queue tomorrow 10:00` (note captured; scheduling TODO)
- `help`

Reply commands must be sent as a reply to the original approval message, which includes machine-readable refs:
- `RefDraft: <draft_id>`
- `RefContent: <content_item_id>`

Supported reply commands in v1: `post`, `regen`, `shorter`, `stronger`, `reject`, `queue`, `help` (plus optional `queue ...` note text).


## Operator flow (manual MVP)

1. Ingest topics: `python scripts/manual_ingest.py --channel OnlyAiOps --topic "..."`
2. Run planner + draft + review jobs using your existing scripts/service wiring.
3. Run one-command operator cycle (planner -> draft -> review -> dispatch):
   - `python scripts/run_operator_cycle.py --channel only_ai_ops_en`
4. Approver acts from Telegram using inline buttons or reply commands.
5. `ApprovalService` resolves action and publishes/rewrites accordingly.

## Run locally

```bash
cd onlycuts
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

Run API:

```bash
uvicorn onlycuts.app.main:app --reload
```

Run one-command operator cycle:

```bash
python scripts/run_operator_cycle.py --channel only_ai_ops_en
```

Alternative API trigger:

```bash
curl -X POST http://localhost:8000/admin/run-job -H "content-type: application/json" -d '{"job_name":"operator_cycle","channel_code":"only_ai_ops_ru"}'
```

Dispatch-only trigger (if planner/draft/review already ran):

```bash
curl -X POST http://localhost:8000/admin/run-job -H "content-type: application/json" -d '{"job_name":"approval_dispatch"}'
```

Run scheduler (stays alive until signal):

```bash
python scripts/run_scheduler.py
```

Manual ingest:

```bash
python scripts/manual_ingest.py --channel OnlyAiOps --topic "Idea 1" --topic "Idea 2"
```

## Verify approval loop locally

1. Insert/create a channel, topic, content item, and reviewed draft (`review_status=passed`) in DB.
2. Send approval dispatch message (or craft callback/message payload).
3. Call `POST /telegram/callback` with an authorized user/chat.
4. Confirm approval + publication records and content/topic status transitions in DB.
