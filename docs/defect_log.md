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

| DEF-002 | YYYY-MM-DD | Sonali | `app/schemas/dream_schema.py` | The file was committed empty, so `DreamCreate` could not be imported | High | Fixed | Commit "Add dream and task schema content" | |
| DEF-003 | YYYY-MM-DD | Sonali | `constants.py`, `task_service.py` | The status word "missed" did not match the SRS, which says "overdue" | Medium | Fixed | Commit "Use SRS status word overdue" | |