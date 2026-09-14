# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Single-file Python CLI for tracking job applications. All logic lives in `src/main.py`; data is stored in `data/jobs.csv`.

## Commands

```bash
pip install openpyxl python-dotenv   # no requirements.txt exists
python src/main.py                   # must be run from the repo root
```

There are no tests, linter, or build configuration.

## Architecture

- `src/main.py` is a menu loop (`if __name__ == "__main__"`) that dispatches to one function per feature: add, view, update status, search, filter, export to Excel, email reminder.
- Every function opens `data/jobs.csv` directly and re-reads the whole file; there is no shared data layer or in-memory model. Updates rewrite the entire file.
- Rows are accessed by positional index: `0=Company, 1=Role, 2=Location, 3=Status, 4=Date`. Changing the column order requires touching every function.
- File paths (`data/jobs.csv`, `job_applications.xlsx`) are relative to the current working directory, not to the script, so running from `src/` creates a separate `src/data/` folder.
- `init_file()` creates the CSV with a header if missing.
- `export_to_excel()` writes `job_applications.xlsx` to the repo root.
- `send_email_reminders()` loads `EMAIL_ADDRESS` and `EMAIL_PASSWORD` from `.env` (via python-dotenv) and sends via Gmail SMTP_SSL on port 465 to the sender's own address, listing rows whose status is `applied`.

## Known issues and pending work

`improvements.txt` tracks requested changes. Relevant facts when working on them:

- Existing CSV rows contain leading spaces after commas (e.g. `" Applied"`). Always read rows via `read_jobs()` and user input via `clean()`, which strip them.
- Matching goes through `fuzzy_match()` (stdlib `difflib`): substring, whole-value ratio, then per-word and word-prefix ratio at a 0.75 threshold. Status search tries exact match first so "Applied" does not return "Not Applied Yet".
- `update_job_status()` lists fuzzy matches and asks which row to update when there are several.
- The README advertises edit and delete, but no such functions exist in `main.py`.

## Out of scope

`karpathy-agent/` is a separate personal knowledge base with its own `karpathy-agent/CLAUDE.md`. Ignore it for job-tracker code work.

