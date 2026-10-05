# Decisions: Search relevance improvements

Append only. Mark superseded entries with `Superseded by Dn (YYYY-MM-DD)`; never delete.

## D1 — 2026-09-03 — Fix parsing before touching ranking

- Decision: P2 (ranking signals) starts only after P1 publishes an evaluation baseline on the fixed parser.
- Reason: 9% of evaluation queries lose a term during tokenization, so ranking experiments on the current parser measure the bug as well as the signal.
- Agreed: product owner in the 2026-09-03 planning call.
