# Aspira – Defect Log

## Purpose
This log records every defect found during development and testing, so the
team can see what went wrong, how it was fixed, and whether it has been
re-tested.

## How to use it
1. Add a new row for each defect, with the next ID number.
2. Fill in every column. Leave "Fixed in" and "Re-tested by" empty until done.
3. The person who fixes a defect must not be the person who re-tests it.

## Severity levels
| Level | Meaning |
|---|---|
| High | Feature does not work, or data is lost |
| Medium | Feature works but gives a wrong or confusing result |
| Low | Cosmetic or minor problem |

## Defects

| ID | Date found | Found by | File or feature | What went wrong | Severity | Status | Fixed in | Re-tested by |
|---|---|---|---|---|---|---|---|---|
| DEF-001 | 2026-11-15 | Sonali | `app/schemas/task_schema.py` | The file was committed empty, so importing `TaskCreate` failed with an ImportError | High | Fixed | Commit "Add dream and task schema content" | |
| DEF-002 | | | | | | | | |