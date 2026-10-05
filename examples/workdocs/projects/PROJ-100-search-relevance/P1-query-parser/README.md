---
kind: project
title: P1 query parser fixes
status: active
jira: [PROJ-110, PROJ-111]
repos: [webapp]
branches: [feature/PROJ-110-tokenizer]
created: 2026-09-03
---

# P1 query parser fixes

Current state: [HANDOFF.md](HANDOFF.md). History: [LOG.md](LOG.md).

## Objective

No evaluation query loses a term during parsing, and the parser handles quoted phrases and hyphenated product codes. Done when the evaluation set shows zero dropped terms and the baseline is published for P2.

## Scope

- In: `webapp:src/search/tokenizer.ts`, `webapp:src/search/query.ts`, their tests.
- Out: ranking, synonyms (PROJ-120).

## Glossary

- Dropped term: a query token that never reaches the index lookup.

## Document map

| Need | Document |
|---|---|
| Current status and next action | [HANDOFF.md](HANDOFF.md) |
| What was done, in order | [LOG.md](LOG.md) |
| Why terms are dropped today | [01-current-parser-analysis.md](01-current-parser-analysis.md) |
| Fuzz-testing sub-task | [tasks/T01-tokenizer-fuzz/HANDOFF.md](tasks/T01-tokenizer-fuzz/HANDOFF.md) |
