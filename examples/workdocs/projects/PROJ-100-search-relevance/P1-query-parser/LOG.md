# Log: P1 query parser fixes

Newest first. Append only.

## 2026-09-24 — Claude Code (webapp-1) — hyphen fix lands, 1.4% left

- Done: split on hyphens only between letters; product codes like `AB-1200` stay one token.
- Found: dropped-term rate 9.1% → 1.4%; all remaining cases are quoted phrases ending in punctuation.
- Evidence: `data/PROJ-100-search-relevance/P1-query-parser/eval-20260924/summary.json`
- Docs changed: HANDOFF (status, next action), 01 (section 3 list of remaining queries)
- Commits: webapp@4f2a9c1 on feature/PROJ-110-tokenizer

## 2026-09-22 — Claude Code (webapp-1) — first fix attempt reverted

- Done: tried normalising all Unicode dashes to spaces before tokenizing.
- Found: fixed 40 queries but split 112 product codes; reverted.
- Evidence: `data/PROJ-100-search-relevance/P1-query-parser/eval-20260922/summary.json`
- Commits: webapp@9b81d07 (reverted by webapp@1c3e5aa) on feature/PROJ-110-tokenizer

## 2026-09-18 — Codex (webapp-2) — analysis of dropped terms

- Done: classified the 418 dropped-term queries in the evaluation set.
- Docs changed: added 01-current-parser-analysis.md, README map; dispatched T01.

## 2026-09-03 — wd — created

- Done: scaffolded with `wd new`.
