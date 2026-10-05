---
kind: note
title: p95 search latency spike on 2026-09-19
status: done
jira: [PROJ-150]
repos: [webapp]
branches: []
created: 2026-09-20
---

# p95 search latency spike on 2026-09-19

p95 rose from 180 ms to 950 ms between 14:05 and 14:40 UTC. The catalogue import started at 14:02 and rebuilt the facet cache synchronously on the request path; latency returned to normal when the import finished at 14:38.

Fix proposed in PROJ-150: rebuild the cache in the import job, not on first request. No further work in this note; the fix is tracked in the ticket.
