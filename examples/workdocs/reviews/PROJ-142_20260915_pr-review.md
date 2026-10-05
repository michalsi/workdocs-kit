---
kind: review
title: Review of PR #142 (cache search facets)
status: done
jira: [PROJ-142]
repos: [webapp]
branches: []
created: 2026-09-15
---

# Review of PR #142 (cache search facets)

## 2026-09-15 — first pass

- Blocking: the cache key omits the user's locale (`webapp:src/search/facets.ts:31`), so facet labels leak across languages.
- Non-blocking: TTL of 24 h is longer than the catalogue import interval (6 h); stale counts are possible after an import.
- Tests cover a hit and a miss, not invalidation after import.

## 2026-09-17 — second pass

- Locale is now part of the key; verified with the new test `facets.locale.test.ts`.
- TTL reduced to 6 h. Approved.
