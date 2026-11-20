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
- The router and service tests (`test_routers_db.py`) use a temporary SQLite database in memory with Ananya's models and repositories; `aspira.db` is never touched. The earlier fake store (`backend/tests/fake_repository.py`) is no longer used by the routers.
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
| Dream, journal, task and analytics services and routers | `test_routers_db.py` | 18 tests through FastAPI on a temporary SQLite database with Ananya's repositories: add, list, view, delete; journal order and filter; allowed status change; completed refused (FR-EV-01); another user's dream or task returns 404 (DR-01); weekly counts use only the newest roadmap; deleting a dream removes its tasks (DR-02) | 18 pass |
| Roadmap schema | `roadmap_schema.py` | A roadmap with a milestone and a task is accepted; the source "copied" is rejected | Pass |
| Scope guard (Riya's file) | `test_scope_guard.py` | 14 tests passed: normal and Hindi questions allowed; empty, too-long (1500 limit), injection (also with hidden characters) and spam refused; control characters removed; the prompt tag cannot be closed; off-topic marker found and removed | Pass; 2 findings (xfail) |
| Chat service (Riya's file) | `test_chat_service.py` | 11 tests passed with a fake AI: normal answer, off-topic marker, bad messages never reach the AI, history and wrapped message sent, history trimmed to start with the user, streaming (normal, off-topic, injection) | Pass |
| Disclaimers (Riya's file) | `test_disclaimer_service.py` | 15 tests passed: topic detection (salary, guarantee, legal, health, finance), answer text unchanged, no notice for plain advice, one notice per topic, fixed messages | Pass; 5 findings (xfail) |
| Security and auth (Riya's file) | `test_security_and_auth.py` | 36 tests | Pass |
| Gemini client (Riya's file) | `test_ai_client.py` | 29 tests with a fake Gemini: retries, circuit breaker, safety and empty answers, structured JSON, streaming | Pass |
| Roadmap generation (Riya's file) | `test_roadmap_generation.py` | 43 tests with a fake AI | Pass |
| Roadmap regeneration (Riya's file) | `test_roadmap_regeneration.py` | 19 tests with a fake AI | Pass |
| Roadmap prompts (Riya's file) | `test_roadmap_prompts.py` | 11 tests | Pass |
| Automated suite | `backend/tests/` | `pytest` in `backend/` on `main` after all test branches were merged: 201 passed, 7 xfailed (known findings, see section 4) | Pass |

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
| DEF-011 | The file is empty, and the app stops at start without `SECRET_KEY` (at least 32 characters) and `GEMINI_API_KEY`. The setup guide has step 3b, but the template is still missing | Medium | Open (Riya) |
| DEF-012 | `RoadmapResponse` requires `version` and `disclaimer`, but Ananya's Roadmap table has neither (SRS section 5.1 names them), so roadmap endpoints returning her objects would fail validation | Medium | Open (team decision) |

The full log is in `docs/defect_log.md`.

## 5. Limitations
- The checks for the shared utilities and schemas (date helpers, constants, errors, task, dream, auth, chat and roadmap schemas, status rules, weekly calculation) were direct checks run by hand by the code's author. `test_routers_db.py` is automated, but it was also written by the author of the routers it tests. Under the team rule that nobody tests their own code, Riya should review both.
- The M4 tests (scope guard, chat service, disclaimers) were written and run
  by Sonali against Riya's code. They run automatically in pytest.
- A test marked xfail means "expected to fail": it describes the correct
  behaviour that the code does not have yet. Each one is logged as a defect.
- Router and service tests now run against a real SQLite database (temporary, in memory). They have not been run against PostgreSQL, or through the running server.
- The logged-in user is a temporary demo user (id 1) in `dream_router.get_current_user_id`, because the login helper (`dependencies.py`) is not in `main` yet. The weekly graph counts only the newest roadmap of a dream, because the Roadmap table has no active flag; the SRS says a dream has one roadmap, but the tables allow several.
- Under SRS FR-EV-01 a task can become completed only through accepted
  evidence. The evidence service is not built yet, so no task can reach
  "completed" in the running app, and the weekly graph shows zero completed.
- Deleting a dream also deletes its roadmaps, milestones and tasks (SRS DR-02); this is tested for tasks in `test_routers_db.py`. Evidence, resources and quiz tables do not exist yet.
- `RoadmapResponse` requires `version` and `disclaimer`, but Ananya's Roadmap table has neither, so roadmap endpoints are not tested here.
- Tested since this report was first written: `security.py` (36 tests), `ai_client.py` (29), `roadmap_generator.py` (43), `roadmap_regenerator.py` (19) and the roadmap prompts (11). Not tested by me yet: the frontend, the readiness score, and the auth, roadmap and chat services and routers that are not in `main`. Whether `intake_service.py` is covered inside the roadmap generation tests has not been checked.
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
