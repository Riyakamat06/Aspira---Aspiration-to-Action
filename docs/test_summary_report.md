# Aspira – Test Summary Report: M2 Modules Owned by Sonali

**Prepared by:** Sonali
**Date:** [date]
**Code tested:** `main` branch, after the merge of `feature/evidence-tracking`

## 1. Purpose
This report summarises the checks run on the M2 files owned by Sonali: the
shared utilities, schemas, dream, journal, task and analytics logic, and
their routers. It states what was checked, what was found, and what has not
been tested yet.

## 2. Environment
- GitHub Codespaces, Python 3.14, FastAPI, Pydantic 2.14, pytest 9.2.0
- A temporary in-memory store (`tests/fake_repository.py`) stands in for the
  database, because the M1 models and repositories are not yet available.

## 3. What was checked

| Area | File(s) | Check | Result |
|---|---|---|---|
| Week calculation | `date_utils.py` | The Monday of 18 Nov 2026 is 16 Nov 2026 | Pass |
| Shared words | `constants.py` | A project task needs a GitHub link; statuses are pending, submitted, completed, overdue | Pass |
| Shared errors | `exceptions.py` | NotFoundError gives the message "Dream not found" | Pass |
| Task schema | `task_schema.py` | A valid task is accepted; the task type "homework" is rejected | Pass |
| Dream schema | `dream_schema.py` | A dream with only a title is accepted | Pass |
| Auth and chat schemas | `auth_schema.py`, `chat_schema.py` | A valid sign-up is accepted and its email lower-cased; an email with no "@" is rejected; a valid chat message is accepted | Pass |
| Status rules | `task_service.py` | pending to completed is refused (SRS FR-EV-01); pending to overdue and pending to submitted are allowed | Pass |
| Weekly progress | `analytics_service.py` | 3 tasks gave 2 due / 1 completed in one week and 1 due / 1 completed in the next | Pass |
| Dream and journal logic | `dream_service.py`, `journal_service.py` | Add, list and delete a dream; a journal entry for a missing dream is refused | Pass |
| Dream router | `dream_router.py` | Add 201, list 200, missing 404, delete 204, empty title 422 | Pass |
| Journal router | `journal_router.py` | Add 201, unknown dream 404, list returns the entry | Pass |
| Task router | `task_router.py` | View works, completed refused 400, submitted accepted 200, unknown status 422, missing task 404 | Pass |
| Analytics router | `analytics_router.py` | Weekly data matches the agreed shape; a missing dream gives 404 | Pass |
| Automated suite | `tests/` | `pytest` on `main`: 1 passed (`test_health.py`). The checks above are not yet part of it | Pass (1 test) |

## 4. Defects found
| ID | Summary | Severity | Status |
|---|---|---|---|
| DEF-001 | `task_schema.py` was committed empty, so importing `TaskCreate` failed | High | Fixed |
| DEF-002 | `dream_schema.py` was committed empty | High | Fixed |
| DEF-003 | The status word "missed" did not match the SRS (section 3.4 says "overdue") | Medium | Fixed |

The full log is in `docs/defect_log.md`.

## 5. Limitations
- These were direct checks run by the code's author with a temporary store.
  They are not a replacement for independent testing. Under the team rule
  that nobody tests their own code, the independent tests for these files
  are owned by Riya (M4).
- Nothing has been tested against a real database, because the M1 models and
  repositories were not available.
- The checks were run by hand. Only the health test is automated in pytest.
- The four router connection points (`get_dream_repo`, `get_journal_repo`,
  `get_task_repo`, `get_analytics_repo`) raise a "connect the repository"
  error until M1's repositories are added.
- Under SRS FR-EV-01 a task can become completed only through accepted
  evidence. The evidence service is not built yet, so no task can reach
  "completed" in the running app, and the weekly graph shows zero completed.
- Evidence verification, readiness score, re-planning, reminders and
  resources were not part of this work. The file structure assigns them to
  Riya or marks them "Later".

## 6. Conclusion
The files covered here behaved as specified in the checks above. The next
steps are independent testing by Riya and connection to the real database
once M1 delivers it.