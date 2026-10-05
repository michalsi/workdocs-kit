# workdocs

Personal project and task documentation, kept outside code repos. Rules for agents: `{{kit}}/CONVENTIONS.md`. Active work: [INDEX.md](INDEX.md) (regenerate with `wd index`).

## How to work with it

You give agents tasks. They find the project, read its HANDOFF, and keep the docs current. You only need the prompts below.

| You want to | Say to the agent (any checkout) | What happens |
|---|---|---|
| Start a new project | "start a project for PROJ-1234: <one-line goal>" (ideally on a branch whose name contains the key) | `wd new` creates `projects/PROJ-1234-<slug>/` with README, HANDOFF, LOG and links the current branch |
| Start a sub-project of an epic | "start a project for PROJ-1234 under the search epic" | same, inside the epic folder |
| Resume existing work | "continue phase-2", "where are we on PROJ-1234?" | `wd where` finds the folder; the agent reads HANDOFF and reports status and next action |
| Review someone's PR | "review PR #123 (PROJ-456) and save the review" | one file in `reviews/`; a second round is appended to it. A PR of your own project goes in that project's `reviews/` |
| Save a one-off analysis | "write this up as a note" | one file in `notes/` |
| Record something now | "log this", "record this decision", "update the handoff" | LOG entry / DECISIONS entry / HANDOFF refresh |
| Finish a project | "close this project" | `status: done`, final LOG entry; the folder stays where it is |
| Clean loose notes out of a repo | "move my loose notes out of webapp" | `wd audit`, a proposed mapping for you to approve, then the move |

Two habits make it reliable:

- **Before you leave a long session, say "update the handoff".** Agents write as they go and a Stop hook reminds them, but Esc, closing the terminal, or running out of context can still cut off the last few minutes.
- **On a fresh branch, mention the Jira key once.** After that, sessions on that branch are matched to the project automatically (`[workdocs] … →` line at session start).

What happens automatically in Claude Code:

- Session start: the project mapped to the current branch is named, so the agent knows where its docs are. After a context compaction the agent is reminded to write down anything from before the compaction.
- During work: after about 20 tool calls in a project without a LOG/HANDOFF update, the agent is stopped once and asked to record anything durable (`NUDGE_AFTER` in `~/.config/workdocs/config`).
- Session end: everything in `~/workdocs` is committed to its local git repo.

Codex and Cursor follow the same rules from their global instructions but have none of these hooks, so "update the handoff" matters more there.

## Commands you might use yourself

| Command | Does |
|---|---|
| `wd ls` / `wd ls --all` | active (or all) projects with last log date and next action |
| `wd where [KEY-or-name]` | folder for the current branch, or for a key/name |
| `wd new PROJ-1234-slug [--epic <epic>]` | scaffold a project by hand |
| `wd link <project>` | map the current branch to an existing project |
| `wd data <project>` | path for bulky files (git-ignored `data/…`) |
| `wd audit` | untracked files left in your checkouts |
| `wd lint`, `wd index`, `wd checkpoint -m "…"` | check, regenerate INDEX.md, commit |
| `git -C ~/workdocs log -p` | see exactly what agents changed; revert if wrong |

## Layout

`projects/` (epics and projects, each with README, HANDOFF, LOG, optional DECISIONS and numbered docs), `reviews/`, `notes/`, `archive/` (bulk dumps, unchanged), `data/` (git-ignored artifacts, mirrors the project paths).

## Machine-specific notes

- Backup: none yet.
