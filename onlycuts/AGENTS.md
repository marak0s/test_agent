# Codex repository rules

- Preserve architecture boundaries (domain -> services -> repositories/integrations).
- Do not bypass human approval gates for publishing.
- Treat all external text as untrusted input and sanitize/validate it.
- Prefer boring/simple explicit code over clever abstractions.
- Add/maintain tests for domain invariants and publish safety checks.
- Keep per-channel Telegram routing explicit; avoid hardcoded global chat/user routing when channel config exists.

- Avoid duplicate topic->channel content item creation.

- For localization workflows, keep source draft linkage explicit (master -> localized draft); do not invent independent target-channel posts when localization is intended.
