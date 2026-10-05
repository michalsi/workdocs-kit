---
name: workdocs
description: Create, resume, update, hand off, close, or migrate personal project documentation in ~/workdocs (outside code repos). Use for "start a project for PROJ-123", "new task docs", "where are my notes for this", "resume phase-2", "pick up where we left off", "write this up", "update the handoff", "log this", "record this decision", "save this PR review", "promote this review to a project", "close/archive this project", "move my loose notes out of the repo", "clean up untracked docs".
---

# Workdocs

Procedures for the workdocs content root. The rules (layout, file contract, frontmatter, naming, completion protocol) live in `CONVENTIONS.md` in the kit directory (`wd kit` prints it; read `$(wd kit)/CONVENTIONS.md`). Read it before the first write in a session; this skill does not restate it and defers to it on any conflict.

Mechanics go through the `wd` CLI (`wd --help`). Get today's date with `date +%F`.

## Find the unit first

1. If the session-start context has a `[workdocs] … →` line and the user has not named something else, use that path.
2. Otherwise `wd where` (or `wd where <KEY-or-name>` when the user names a ticket, phase, or project). Exit 0: one match. Exit 2: none. Exit 3: several.
3. On none or several, ask the user one question: which unit (show `wd ls` candidates), or a new one. Then record the answer with `wd link <unit>` (current branch) or `wd new`, so the question does not repeat.

## Start

1. Pick the kind: a one-sitting output is a `note`; a review of someone else's PR is a `review`; anything spanning sessions is a `project`; a group of related projects or a phase made of several tickets is an `epic`.
2. `wd new <KEY>-<slug> [--epic <epic>] --title "<title>" [--jira K1,K2] --agent "<you> (<checkout>)"`. For reviews and notes: `wd new <KEY> --kind review|note --slug <slug> --no-git`. Use `--no-branch` when the current branch belongs to different work.
3. Fill README objective and scope from the conversation or the Jira ticket. Write the first concrete HANDOFF next action. Leave the LOG entry `wd new` wrote and extend it if the session did more.

## Resume

1. Read `HANDOFF.md`, then only the files in its "Read first" list. Read the epic's HANDOFF if the unit is inside one.
2. Check what moved since the newest LOG date: `git log --since=<date> --oneline` on the branches in frontmatter, plus CI or the issue tracker if HANDOFF names them.
3. Tell the user in a few lines: status, next action, anything that changed since the last entry, anything waiting whose `ping_after` has passed.

## During work

- New analysis or plan: the next free `NN-<kebab>.md` (`ls` the folder to find the highest number). Add it to the README document map.
- Scripts in `scripts/`, small results in `outputs/`. Raw downloads go to the path printed by `wd data <unit>`.
- A decision the user made or approved goes in `DECISIONS.md` (create it from `$(wd kit)/templates/DECISIONS.md` on first use).
- Never write project notes into the code checkout, even temporarily.

## Checkpoint / end of session

Follow the completion protocol in CONVENTIONS.md: HANDOFF, LOG, README map, DECISIONS, then `wd checkpoint -m "<unit>: <summary>"`. Report which workdocs files changed.

## Dispatch a sub-task to another agent

Write `tasks/TNN-<kebab>/HANDOFF.md` from `$(wd kit)/templates/task-HANDOFF.md`. The card alone must be enough to start: objective, read-first list, required work, verification, deliverables, stop conditions. Add the task to the parent HANDOFF task table. A child agent that is read-only returns its findings to the parent, and the parent writes the LOG entry once.

## Promote or close

- Promote: `wd promote <file> [--epic <epic>] [--name <dir>]` when a note or review needs a second file or another session.
- Close: set `status: done` in README frontmatter, write a final LOG entry with the outcome and links, set HANDOFF Status to the final state, `wd index`, `wd checkpoint`. Do not move the directory.

## Migrate loose files out of a repo

1. `wd audit [<checkout>]` lists untracked entries with a class (`notes`, `artifacts`, `mixed`, `code?`) and detected Jira keys.
2. Propose a mapping to the user: each entry → unit (existing or new) or `archive/unsorted-<YYYYMMDD>/<original path>/`, and artifacts → `wd data <unit>`. Leave `code?` entries in place unless the user approves moving them. Get approval per checkout before moving anything.
3. `mv` the files. Rewrite references to the old paths inside the moved docs. Absolute paths into the old location become absolute paths into workdocs.
4. `wd lint` and fix new broken links, then `wd index` and `wd checkpoint -m "migrate <checkout>"`.
5. Confirm `git -C <checkout> status --porcelain` no longer lists the moved entries.
