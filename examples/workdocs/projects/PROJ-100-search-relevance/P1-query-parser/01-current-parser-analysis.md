# Why the parser drops terms

Analysis of the 418 evaluation queries (of 4,600) where at least one token never reaches the index lookup. Evaluation set at `webapp:scripts/eval/queries.jsonl@2d7e0b4`.

## 1. Classification

| Cause | Queries | Share of dropped |
|---|---|---|
| Hyphen splits a product code, second half shorter than the 2-char minimum | 353 | 84% |
| Quoted phrase ends with `.`, `,` or `?` inside the quotes | 64 | 15% |
| Other (emoji, zero-width space) | 1 | <1% |

## 2. Where it happens

- `webapp:src/search/tokenizer.ts:48` splits on every `-` before the minimum-length filter runs.
- `webapp:src/search/query.ts:112` (`parsePhrase`) treats the closing quote as part of the last token when punctuation precedes it.

## 3. Remaining failing queries after the hyphen fix

Twelve representative cases for unit tests, e.g. `"red running shoes."`, `"size 10, wide"`, `"is it waterproof?"`. Full list: `data/PROJ-100-search-relevance/P1-query-parser/eval-20260924/remaining.txt`.
