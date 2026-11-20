# Aspira – Test Summary Report: M2 Modules Owned by Sonali

**Prepared by:** Sonali
**Date:** 2026-11-19
**Code tested:** `main` at commit 689da43, plus Sonali's branch `sonali/m4-tests`

## 1. Purpose
This report summarises the checks run on the M2 files owned by Sonali (the
shared utilities, schemas, dream, journal, task and analytics logic, and
their routers) and the independent tests Sonali wrote for Riya's scope guard,
chat service and disclaimers. It states what was checked, what was found, and
what has not been tested yet.

## 2. Environment
- GitHub Codespaces, Python 3.14, FastAPI, Pydantic 2.14, pytest 9.2.0
- A temporary in-memory store (`backend/tests/fake_repository.py`) stands in
  for the database, because the M1 models and repositories are not yet
  available in `main`.
- A fake AI stands in for Gemini in every test. No real model was called.

## 3. What was checked

| Area | File(s) | Check | Result |
|---|---|---|---|
| Week calculation | `date_utils.py` | The Monday of 18 Nov 2026 is 16 Nov 2026 | Pass |
| Shared words | `constants.py` | A project task needs a GitHub link; statuses are pending, submitted, completed, overdue | Pass |
| Shared errors | `exceptions.py` | NotFoundError gives the message "Dream not found" | Pass |
| Task schema | `task_schema.py` | A task linked to a milestone (`milestone_id`) is accepted; `task_type` is optional until M1 adds it | Pass |
| Dream schema | `dream_schema.py` | A dream with only a title is accepted | Pass |
| Auth and chat schemas | `auth_schema.py`, `chat_schema.py` | A valid sign-up is accepted and its email lower-cased; an email with no "@" is rejected; a valid chat message is accepted | Pass |
| Status rules | `task_service.py` | pending to completed is refused (SRS FR-EV-01); pending to overdue and pending to submitted are allowed | Pass |
| Weekly progress | `analytics_service.py` | 3 tasks gave 2 due / 1 completed in one week and 1 due / 1 completed in the next | Pass |
| Dream and journal logic | `dream_service.py`, `journal_service.py` | Add, list and delete a dream; a journal entry for a missing dream is refused | Pass |
| Dream router | `dream_router.py` | Add 201, list 200, missing 404, delete 204, empty title 422 | Pass |
| Journal router | `journal_router.py` | Add 201, unknown dream 404, list returns the entry | Pass |
| Task router | `task_router.py` | View works, completed refused 400, submitted accepted 200, unknown status 422, missing task 404 | Pass |
| Analytics router | `analytics_router.py` | Weekly data matches the agreed shape; a missing dream gives 404 | Pass |
| Roadmap schema | `roadmap_schema.py` | A roadmap with a milestone and a task is accepted; the source "copied" is rejected | Pass |
| Scope guard (Riya's file) | `test_scope_guard.py` | 14 tests passed: normal and Hindi questions allowed; empty, too-long (1500 limit), injection (also with hidden characters) and spam refused; control characters removed; the prompt tag cannot be closed; off-topic marker found and removed | Pass; 2 findings (xfail) |
| Chat service (Riya's file) | `test_chat_service.py` | 11 tests passed with a fake AI: normal answer, off-topic marker, bad messages never reach the AI, history and wrapped message sent, history trimmed to start with the user, streaming (normal, off-topic, injection) | Pass |
| Disclaimers (Riya's file) | `test_disclaimer_service.py` | 15 tests passed: topic detection (salary, guarantee, legal, health, finance), answer text unchanged, no notice for plain advice, one notice per topic, fixed messages | Pass; 5 findings (xfail) |
| Automated suite | `backend/tests/` | `pytest` in `backend/`: 45 passed, 7 xfailed (known findings, see section 4). The 5 tests beyond the three M4 files come from `test_health.py` and `test_m2_smoke.py` | Pass |

## 4. Defects found
| ID | Summary | Severity | Status |
|---|---|---|---|
| DEF-001 | `task_schema.py` was committed empty, so importing `TaskCreate` failed | High | Fixed |
| DEF-002 | `dream_schema.py` was committed empty | High | Fixed |
| DEF-003 | The status word "missed" did not match the SRS (section 3.4 says "overdue") | Medium | Fixed |
| DEF-004 | Chat limit was 2000 in `chat_schema.py` but 1500 in `config.py` | Medium | Fixed (re-test by Riya) |
| DEF-005 | `scope_guard.py` blocks a normal sentence containing "new instructions:" | Low | Open |
| DEF-006 | `scope_guard.py` blocks a normal sentence containing "you are now" | Low | Open |
| DEF-007 | `disclaimer_service.py` gives a salary notice for "package" (software) | Low | Open |
| DEF-008 | `disclaimer_service.py` gives a salary notice for "per month" (study hours) | Low | Open |
| DEF-009 | `disclaimer_service.py` gives a finance notice for "invest time" | Low | Open |
| DEF-010 | `disclaimer_service.py` adds no notice for lawyer or doctor answers (SRS section 3.6 and NFR-12); to confirm with Riya | Medium | Open |

The full log is in `docs/defect_log.md`.

## 5. Limitations
- The checks in section 3 down to the roadmap schema were direct checks run by
  the code's author with a temporary store. They are not a replacement for
  independent testing. Under the team rule that nobody tests their own code,
  the independent tests for these files are owned by Riya (M4).
- The M4 tests (scope guard, chat service, disclaimers) were written and run
  by Sonali against Riya's code. They run automatically in pytest.
- A test marked xfail means "expected to fail": it describes the correct
  behaviour that the code does not have yet. Each one is logged as a defect.
- Nothing has been tested against a real database, because the M1 models and
  repositories are not in `main`.
- The four router connection points (`get_dream_repo`, `get_journal_repo`,
  `get_task_repo`, `get_analytics_repo`) raise a "connect the repository"
  error until M1's repositories are added.
- Under SRS FR-EV-01 a task can become completed only through accepted
  evidence. The evidence service is not built yet, so no task can reach
  "completed" in the running app, and the weekly graph shows zero completed.
- Deleting a dream does not yet delete its roadmaps, tasks, evidence and
  analytics (SRS FR-MD-04). This needs a cascading delete in M1.
- Not yet tested: `security.py`, `ai_client.py`, `intake_service.py`,
  `roadmap_generator.py` and `roadmap_regenerator.py` (in `main`, not yet read
  or tested), the readiness score, and the frontend.
- Not yet checked: whether generated roadmaps carry the disclaimer for
  medical, legal and other regulated fields (SRS FR-RG-08).
- Evidence verification, re-planning, reminders and resources were not part of
  this work. The file structure assigns them to Riya or marks them "Later".

## 6. Conclusion
The files covered here behaved as specified in the checks above. The
independent tests of Riya's scope guard, chat service and disclaimers found 6
open problems, listed in section 4. Roadmap generation, the AI client, auth
and the frontend still need testing, and the real database connection depends
on M1.
