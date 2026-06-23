# Task Intake

Purpose: personal and project-local source-first task intake. Use this file to preserve the original task assignment before AI analysis, task splitting, status tracking, or changelog writing.

This file supports handoff context, interrupted session recovery, and human review of whether AI misunderstood, deleted, or over-compressed a task. It is not the company official version number, not an MR-ready changelog, not a replacement for requirements, task-board, testing, risk-register, or traceability, and must not contain secrets.

## When to Use

Create or update a source record when work comes from:

- leader-plan-cell
- wechat
- meeting
- document
- manual-note

Use this before turning the assignment into requirements, task-board items, change artifacts, or release notes.

## Source Record Template

```text
Source ID: SRC-YYYYMMDD-001
Source Type: leader-plan-cell | wechat | meeting | document | manual-note
Received At: YYYY-MM-DD HH:MM
Sender / Source: <name or source label>
Original Location: <chat, meeting note, document path, plan row, or other pointer>
Human Review: pending | confirmed | corrected | rejected
Confidentiality: normal | sensitive-redacted
Derived Task IDs: TASK-001, BUG-001, FEAT-001
```

### Original Text

Paste the original assignment here after redaction. Do not replace it with only an AI summary.

### Responsibility Split

| Person / Role | Responsibility | Confirmation |
| --- | --- | --- |
| <name or role> | <responsibility> | pending |

### Time Window

| Field | Value |
| --- | --- |
| Expected start | TBD |
| Expected finish | TBD |
| Deadline / checkpoint | TBD |
| Time ambiguity | TBD |

### AI Interpretation

- Parsed intent:
- Scope:
- Out of scope:
- Assumptions:
- Risks:

### Derived Tasks

| Task ID | Title | Source ID | Status | Notes |
| --- | --- | --- | --- | --- |
| TASK-001 | TBD | SRC-YYYYMMDD-001 | Todo | TBD |

### Open Questions

| Question | Why it matters | Owner | Status |
| --- | --- | --- | --- |
| TBD | TBD | TBD | Open |

### Human Review Status

| Field | Value |
| --- | --- |
| Human Review | pending |
| Reviewer | TBD |
| Review Notes | TBD |
| Corrected Interpretation | TBD |

## Redaction Rules

- Do not keep account names, passwords, tokens, certificates, private keys, internal environment addresses, or sensitive configuration values in this file.
- If the original text contains sensitive information, redact it before writing and set `Confidentiality: sensitive-redacted`.
- If the original assignment has not been manually confirmed, keep `Human Review: pending`; do not mark it as `confirmed`.
- `requirements.md` records requirement facts; it does not replace this source ledger.
- `task-board.md` records derived task status; derived tasks must link back to `Source ID`.
- `changelog.md` records completed version changes; it does not replace original task assignment records.
