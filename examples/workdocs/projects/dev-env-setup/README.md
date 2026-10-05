---
kind: project
title: Local dev environment with seeded search index
status: done
jira: []
repos: [webapp]
branches: []
created: 2026-08-25
---

# Local dev environment with seeded search index

Current state: [HANDOFF.md](HANDOFF.md). History: [LOG.md](LOG.md).

## Objective

`make dev` brings up the app with a search index seeded from an anonymised 50,000-product sample, in under five minutes on a laptop.

## Scope

- In: compose file, seed script, README section in the repo.
- Out: CI images.
