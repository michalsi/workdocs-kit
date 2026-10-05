# Handoff: P1 query parser fixes

## Status (2026-09-24)

The hyphen fix is on `feature/PROJ-110-tokenizer` and drops dropped-term queries from 9.1% to 1.4% of the evaluation set. The remaining 1.4% are quoted phrases with trailing punctuation (PROJ-111).

## Next action

1. Handle trailing punctuation inside quoted phrases in `webapp:src/search/query.ts:parsePhrase`, add the 12 failing queries listed in [01-current-parser-analysis.md](01-current-parser-analysis.md) section 3 as unit tests, then rerun the evaluation set.

## Blocked / waiting

- Fuzz corpus from T01 — waiting on the sub-agent run; not blocking the next action.

## Authorization

- Allowed: commits and pushes to `feature/PROJ-110-tokenizer`; running the evaluation set locally.
- Not allowed without explicit approval: opening the PR, changing shared CI config.

## Read first

1. [README.md](README.md)
2. [01-current-parser-analysis.md](01-current-parser-analysis.md)
3. Epic: [../HANDOFF.md](../HANDOFF.md)

## Tasks

| Task | Status | Depends on | Card |
|---|---|---|---|
| T01 tokenizer fuzzing | In progress | — | [tasks/T01-tokenizer-fuzz/HANDOFF.md](tasks/T01-tokenizer-fuzz/HANDOFF.md) |

## Project rules

- Do not change tokenizer output for queries that already pass; the evaluation diff must show only fixed queries.
