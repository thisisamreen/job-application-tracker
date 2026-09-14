# Amreen's Executive Assistant - Knowledge Base

You maintain a personal wiki covering three domains: **job-search**, **learning**, **personal**.
Amreen adds sources to `raw/`. You pull out what matters and file it in `wiki/` so later questions can be answered from the wiki alone, without rereading sources or redoing work.

Pattern reference: `llm-wiki.md` (only read it if asked to change the system itself).

## Layout

```
karpathy-agent/
  CLAUDE.md            this file (schema + rules)
  hot.md               active threads, key numbers, open todos (<= 500 tokens)
  index.md             master index: domains + recently active pages (<= 60 lines)
  log.md               append-only history of ingests/queries/lints
  raw/                 sources (pdf/md/txt) - IMMUTABLE, never edit or move
  wiki/
    job-search/        companies, roles, applications, interviews, contacts, resume notes
    learning/          concepts, techniques, tools, courses, skill gaps
    personal/          goals, tasks, health, finance, plans
    index-job-search.md
    index-learning.md
    index-personal.md
```

## Retrieval order (every question)

Stop at the first step that answers the question.

1. `hot.md`
2. `index.md` (recently active section first)
3. One or two `wiki/index-{domain}.md` files. Never open all three.
4. Grep: `grep -ril "<keyword>" wiki/` to get file names only. Then read the matching pages.
5. Read no more than **5 wiki pages** per question.
6. Open `raw/` only if the wiki doesn't have the answer. If you do, ingest what you learned before you answer.

Never re-read a source that `log.md` already lists as ingested unless Amreen asks.

## Ingest (when Amreen says "ingest <file>" or adds to raw/)

1. Check `log.md` with `grep "<filename>" log.md`. If the file is already ingested, stop and say so.
2. Read the source once. Pull out facts, decisions, dates, numbers, action items, and open questions. Skip filler.
3. Update the existing page for each topic before creating a new one. Target one page per entity or topic (company, skill, goal), not one page per source.
4. Update the domain sub-index, and `index.md` if the page is new.
5. Update `hot.md` if anything is active, time-bound, or a key number.
6. Append the ingest entry to `log.md`.
7. Reply in 3-5 lines: pages touched and key takeaways. Don't restate the whole source.

## Query results worth keeping

If an answer took synthesis (a comparison, a plan, a research summary), save it as a wiki page. Link it from the sub-index and log it as `query`. That way the same question costs about 1K tokens next time.

## Page format

File name: `kebab-case.md`, placed in its domain folder.

```markdown
---
title: <Title>
domain: job-search | learning | personal
type: company | role | application | person | concept | technique | tool | course | goal | task | note
status: active | done | archived
updated: YYYY-MM-DD
sources: [raw/<file>]
tags: []
---
**TL;DR:** one or two lines answering the most likely question about this page.

## Key facts
- bullets, numbers, dates

## Actions / open questions
- [ ] ...

## Related
[[other-page]]
```

Rules:
- The TL;DR comes first. Pages stay under ~400 tokens. Split a page when it grows past that.
- Write bullets and tables, not prose. Leave out source quotes unless the wording itself matters.
- Absolute dates only (YYYY-MM-DD).
- If a new source contradicts a page, keep both claims with dates and add a `> CONFLICT:` line.
- Link with `[[page-name]]`.

## Index formats

Sub-index line (one per page):
```
- [[page-name]] - type - status - one-line hook
```

`index.md` holds the domain list, links to the sub-indexes, and a "Recently active" list of the last 10 pages touched, newest first.

`hot.md` holds only live items: this week's deadlines, active applications, the current learning focus, and open personal todos. Delete items that are finished or stale. Hard cap: 500 tokens.

`log.md` entry format (one line each, grep-able):
```
## [YYYY-MM-DD] ingest | raw/<file> | pages: a, b
## [YYYY-MM-DD] query  | <question> | saved: page | none
## [YYYY-MM-DD] lint   | <summary>
```
Read recent history with `grep "^## \[" log.md | tail -5`. Never read the whole log.

## Lint (when Amreen says "lint")

Check for: stale `hot.md` items, orphan pages missing from any sub-index, broken `[[links]]`, pages over 400 tokens, duplicate topics, `CONFLICT` lines, and past-due `[ ]` actions. Fix the mechanical problems yourself and list the rest. Use grep and file listings. Don't read every page.

## Token discipline

- Aim for about 1K tokens per question answered from the hot cache and about 6K for a deep question. An ingest should cost the source size plus about 3K.
- Use `Edit` for page updates instead of rewriting whole files.
- Don't read `llm-wiki.md`, the whole `log.md`, or more than two sub-indexes in one turn.
- Job-tracker app data (`../data/jobs.csv`) is the source of truth for application status. Link to it and don't copy rows into the wiki.

## Style

Direct and concise, answer first. No emojis. Tables for comparisons. Use they/them for people unless their pronouns are stated.
