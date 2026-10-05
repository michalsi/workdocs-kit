# Design notes

Why the kit is shaped the way it is. The rules themselves are in [CONVENTIONS.md](../CONVENTIONS.md).

## Problem

Agent-assisted work on a large codebase produces a lot of written material: investigation notes, plans, review findings, run results, downloaded CI artifacts. Left alone, it accumulates as untracked files inside whichever checkout the agent ran in, so the same project ends up spread over several checkouts, and a new session cannot tell which file is current. Agents also lose state when a session ends or its context is compacted.

## Decisions

| # | Decision | Reason |
|---|---|---|
| D1 | The content root is `~/workdocs`, a local git repo with no remote by default. | Git shows exactly what an agent changed and makes any edit revertible. A git repo inside a cloud-synced folder risks `.git` corruption, and on-demand file streaming slows agent searches; backup is a separate one-way copy. |
| D2 | Bulky material goes to `data/<unit path>/`, which is git-ignored. | Keeps the docs repo small enough to diff. Small derived outputs and scripts stay in the project folder. |
| D3 | Discovery uses the exact branch, then the ticket key in the branch name, then a unique repo match. On none or several, the agent asks once and records the answer with `wd link` or `wd new`. | Branch names usually carry a ticket key, and a per-checkout pointer file would go stale on every branch switch. |
| D4 | A repo-only match counts only when exactly one unit lists that repo. | Otherwise every checkout of a repo matches every project in it. |
| D5 | The always-on rule goes in the global agent instructions; the skill holds procedures; a small CLI does the mechanics. | Skills load only when their description matches the request. The rule that notes go to workdocs has to be present in every session. Mechanics in a CLI give the same result for every agent. |
| D6 | Standard relative markdown links, not `[[wikilinks]]`. | Agents, terminals, IDEs, and Obsidian all resolve relative links. |
| D7 | Finished projects are not moved. `status: done` hides them from `wd ls` and `INDEX.md`. | Moving a folder breaks inbound relative links from other projects. |
| D8 | Phases without an umbrella ticket are sub-projects carrying a list of keys in `jira`. | Long efforts are often split across several tickets with no aggregating one. |
| D9 | `wd lint` checks links only in files workdocs maintains (README, HANDOFF, LOG, DECISIONS, single-file notes and reviews) unless `--all-links` is given. | Imported documents often carry links that were already broken. |
| D10 | Ticket key detection can be restricted to configured prefixes (`JIRA_PROJECTS`), and numbers of 7+ digits are never keys. | File names like `findings-20260529` or `app-2.3.1` otherwise produce false keys. |
| D11 | Claude Code hooks call `wd` by absolute path. | Hook processes do not reliably inherit the interactive PATH. |
| D12 | Docs updates are prompted by a Stop hook after `NUDGE_AFTER` tool calls without a LOG/HANDOFF write, and by a reminder after compaction, not only by an end-of-session rule. | End-of-session instructions are skipped when sessions are closed, interrupted, or compacted. |
| D13 | Hooks never fail: every exception is swallowed and the exit code is 0. | A broken docs hook must not block the agent's real work. |

## What the file contract is for

- `HANDOFF.md` is the only place status lives, and it is overwritten every session. An agent starting cold reads one short file and knows what is true now and what to do next.
- `LOG.md` is append-only and keeps failed attempts. It answers "was this already tried?" without relying on anyone's memory.
- `DECISIONS.md` records what the user agreed to, with where it was agreed, so later sessions do not reopen settled questions.
- Numbered docs hold the long material (analysis, plans) and are never renumbered, so links to them stay valid.

The two-week test in CONVENTIONS.md decides which file a statement goes in: if it would be wrong in two weeks, it is dated evidence (LOG or a numbered doc); if it must stay true, it belongs in README, HANDOFF, or DECISIONS.
