# workdocs (example)

A sample content root with made-up projects, showing what `~/workdocs` looks like after a few weeks of use. Everything here is fictional: the `webapp` repo, the `PROJ-` tickets, and the people.

Try the CLI against it from the kit directory:

```bash
export WORKDOCS_ROOT="$PWD/examples/workdocs"
bin/wd ls --all
bin/wd where PROJ-110
bin/wd where parser -v
bin/wd lint
```

What to look at:

| Path | Shows |
|---|---|
| [projects/PROJ-100-search-relevance/](projects/PROJ-100-search-relevance/HANDOFF.md) | an epic with its own decisions and one sub-project |
| [projects/PROJ-100-search-relevance/P1-query-parser/](projects/PROJ-100-search-relevance/P1-query-parser/HANDOFF.md) | a project mid-flight: numbered analysis doc, task card for a sub-agent, LOG with a failed attempt kept |
| [projects/dev-env-setup/](projects/dev-env-setup/HANDOFF.md) | a finished project without a ticket (`status: done`, hidden from `wd ls`) |
| [reviews/](reviews/) | a single-file review of someone else's PR with two rounds |
| [notes/](notes/) | a one-off analysis |

`data/` is absent because it is git-ignored; in real use `wd data <unit>` creates it.
