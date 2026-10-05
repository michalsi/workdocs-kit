# T01 Handoff: Tokenizer fuzzing

## Status

In progress

## Objective

Find tokenizer inputs that drop or merge terms beyond the cases in the evaluation set, so the P1 fix is not tuned only to known queries.

## Read first

- `../../README.md`
- `../../01-current-parser-analysis.md`
- `webapp:src/search/tokenizer.ts`

## Required work

1. Write a property test that generates queries from the product-title vocabulary plus punctuation and Unicode dashes.
2. Assert that every generated alphanumeric run of 2+ characters appears in the token output.
3. Run 100,000 cases against `feature/PROJ-110-tokenizer`.

## Verification

The property test runs in under 60 s locally and reports each failing input minimised.

## Deliverables

- The test file on the branch.
- A list of failing inputs, grouped by cause, returned to the parent agent.

## Stop conditions

- Stop and hand back if more than 5 distinct causes appear; the parent decides scope.

## Completion record

Files changed, tests run, remaining risks. Then update the parent HANDOFF task table and LOG.
