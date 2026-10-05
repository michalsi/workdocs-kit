---
kind: epic
title: Search relevance improvements
status: active
jira: [PROJ-100]
repos: [webapp]
branches: []
created: 2026-09-01
---

# Search relevance improvements

Current state: [HANDOFF.md](HANDOFF.md). History: [LOG.md](LOG.md). Decisions: [DECISIONS.md](DECISIONS.md).

## Objective

Raise the share of searches where the clicked result is in the top three from 61% to 75% on the product catalogue, measured by the weekly click-position report.

## Scope

- In: query parsing, ranking signals, the offline evaluation set.
- Out: UI changes to the results page; the autocomplete service.

## Sub-projects

| Phase | Tickets | Folder |
|---|---|---|
| P1 query parser | PROJ-110, PROJ-111 | [P1-query-parser/](P1-query-parser/README.md) |
| P2 ranking signals | PROJ-120 (not started) | — |

## Document map

| Need | Document |
|---|---|
| Current status and next action | [HANDOFF.md](HANDOFF.md) |
| What was done, in order | [LOG.md](LOG.md) |
| Decisions that apply to every phase | [DECISIONS.md](DECISIONS.md) |
