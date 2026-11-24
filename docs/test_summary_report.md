# Aspira – Test Summary Report: M2 Modules Owned by Sonali

**Prepared by:** Sonali
**Date:** 2026-11-25
**Code tested:** `main` at commit 8ed35af (after the merge of the evidence switch)

## 1. Purpose
This report summarises the checks run on the M2 files owned by Sonali (the
shared utilities, schemas, dream, journal, task and analytics logic, and
their routers) and the independent tests Sonali wrote for Riya's scope guard,
chat service, disclaimers, security helpers, Gemini client, roadmap
generation, roadmap regeneration and roadmap prompts. It states what was
checked, what was found, and what has not been tested yet.

## 2. Environment
- GitHub Codespaces, Python 3.14, FastAPI, Pydantic 2.14, pytest 9.2.0
- The router and service tests (`test_routers_db.py`) use a temporary SQLite database in memory with Ananya's models and repositories; `aspira.db` is never touched. The earlier fake store (`fake_repository.py`) has been deleted.
- A fake AI stands in for Gemini in the tests Sonali wrote. No real model was called.

## 3. What was checked

| Area | File(s) | Check | Result |
|---|---|---|---|
| Week calculation | `date_utils.py` | The Monday of 18 Nov 2026 is 16 Nov 2026 | Pass |
| Shared words | `constants.py` | A project task needs a GitHub link; statuses are pending, submitted, completed, overdue | Pass |
| Shared errors | `exceptions.py` | NotFoundError gives the message "Dream not found" | Pass |
| Task schema | `task_schema.py` | A task linked to a milestone (`milestone_id`) is accepted; `task_type` is optional until M1 adds it | Pass |
| Dream schema | `dream_schema.py` | A dream with only a title is accepted | Pass |
| Auth and chat schemas | `auth_schema.py`, `chat_schema.py` | A valid sign-up is accepted and its email lower-cased; an email with no "@" is rejected; a valid chat message is accepted; `UserResponse` reads the database column `full_name` into `name` | Pass |
| Status rules | `task_service.py` | With evidence required (the default): pending to completed is refused (SRS FR-EV-01); pending to overdue and pending to submitted are allowed. With `EVIDENCE_REQUIRED=false` (demo): pending, overdue or submitted tasks can be completed and a completed task can go back to pending (5 tests in `test_routers_db.py`) | Pass |
| Weekly progress | `analytics_service.py` | 3 tasks gave 2 due / 1 completed in one week and 1 due / 1 completed in the next | Pass |
| Dream, journal, task and analytics services and routers | `test_routers_db.py` | 23 tests through FastAPI on a temporary SQLite database with Ananya's repositories: add, list, view, delete; journal order and filter; allowed status change; completed refused when evidence is required (FR-EV-01); the evidence switch (5 tests); another user's dream or task returns 404 (DR-01); weekly counts use only the newest roadmap; deleting a dream removes its tasks (DR-02) | 23 pass |
| Roadmap schema | `roadmap_schema.py` | A roadmap with a title, a milestone and a task is accepted; `summary` is optional; the source "copied" is rejected | Pass |
| Scope guard (Riya's file) | `test_scope_guard.py` | 16 tests: normal and Hindi questions allowed; empty, too-long (1500 limit), injection (also with hidden characters) and spam refused; control characters removed; the prompt tag cannot be closed; off-topic marker found and removed; two harmless sentences are no longer blocked (DEF-005, DEF-006) | Pass |
| Chat service (Riya's file) | `test_chat_service.py` | 11 tests with a fake AI: normal answer, off-topic marker, bad messages never reach the AI, history and wrapped message sent, history trimmed to start with the user, streaming (normal, off-topic, injection) | Pass |
| Disclaimers (Riya's file) | `test_disclaimer_service.py` | 20 tests: topic detection (salary, guarantee, legal, health, finance), answer text unchanged, no notice for plain advice, one notice per topic, fixed messages; no false notice for "package", "per month" or "invest time"; lawyer and doctor answers get a notice (DEF-007 to DEF-010) | Pass |
| Security and auth (Riya's file) | `test_security_and_auth.py` | 36 tests: bcrypt hashing, password strength rules, token creation and checking (expired, wrong secret, swapped payload, missing claims, algorithm none) | Pass |
| Gemini client (Riya's file) | `test_ai_client.py` | 29 tests with a fake Gemini: retries, circuit breaker, safety and empty answers, structured JSON, streaming | Pass |
| Roadmap generation and intake (Riya's files) | `test_roadmap_generation.py` | 43 tests with a fake AI: intake answers (17), cleaning of the AI plan (14), repair round (3), prompt (2), cache and single flight (7) | Pass |
| Roadmap regeneration (Riya's file) | `test_roadmap_regeneration.py` | 19 tests with a fake AI: feedback guard, finished tasks kept, week shift, added and removed titles | Pass |
| Roadmap prompts (Riya's file) | `test_roadmap_prompts.py` | 11 tests | Pass |
| Riya's own tests | `test_m2_api.py` (22), `test_readiness.py` (7), `test_defect_fixes.py` (21) | Written by the author of the code, so they are not independent. Not reviewed by Sonali | Pass |
| Automated suite | `backend/tests/` | `pytest` in `backend/` on `main`: 263 passed, no failures, no xfail (14 test files; 208 tests are Sonali's, 50 are Riya's own, 5 are the health and smoke tests) | Pass |

## 4. Defects found
| ID | Summary | Severity | Status |
|---|---|---|---|
| DEF-001 | `task_schema.py` was committed empty, so importing `TaskCreate` failed | High | Fixed |
| DEF-002 | `dream_schema.py` was committed empty | High | Fixed |
| DEF-003 | The status word "missed" did not match the SRS (section 3.4 says "overdue") | Medium | Fixed |
| DEF-004 | Chat limit was 2000 in `chat_schema.py` but 1500 in `config.py` | Medium | Fixed (re-test by Riya) |
| DEF-005 | `scope_guard.py` blocked a normal sentence containing "new instructions:" | Low | Fixed by Riya, re-tested by Sonali |
| DEF-006 | `scope_guard.py` blocked a normal sentence containing "you are now" | Low | Fixed by Riya, re-tested by Sonali |
| DEF-007 | `disclaimer_service.py` gave a salary notice for "package" (software) | Low | Fixed by Riya, re-tested by Sonali |
| DEF-008 | `disclaimer_service.py` gave a salary notice for "per month" (study hours) | Low | Fixed by Riya, re-tested by Sonali |
| DEF-009 | `disclaimer_service.py` gave a finance notice for "invest time" | Low | Fixed by Riya, re-tested by Sonali |
| DEF-010 | `disclaimer_service.py` added no notice for lawyer or doctor answers (SRS section 3.6 and NFR-12) | Medium | Fixed by Riya, re-tested by Sonali |
| DEF-011 | `backend/.env.example` was empty, so a new teammate had no template for the required settings | Medium | Fixed by Riya, re-tested by Sonali |
| DEF-012 | `RoadmapResponse` requires `version` and `disclaimer`, but Ananya's Roadmap table has neither (SRS section 5.1 names them), so roadmap endpoints returning her objects would fail validation | Medium | Open (team decision) |
| DEF-013 | POST /dreams returned 500 (NoReferencedTableError) when the server loaded only the routers, because the model files were not imported | Medium | Fixed (`main.py` calls `init_db` at start-up), re-tested by Sonali |

The full log is in `docs/defect_log.md`.

## 5. Limitations
- The checks for the shared utilities and schemas (date helpers, constants, errors, task, dream, auth, chat and roadmap schemas, status rules, weekly calculation) were direct checks run by hand by the code's author. `test_routers_db.py` is automated, but it was also written by the author of the routers it tests. Under the team rule that nobody tests their own code, Riya should review both.
- The M4 tests in section 3 were written and run by Sonali against Riya's code. They run automatically in pytest. Where an AI is involved, a fake AI is used.
- No xfail tests remain. The 7 tests that documented DEF-005 to DEF-010 passed after Riya's fixes (pytest showed 7 xpassed), and their xfail marks were then removed.
- Router and service tests run against a real SQLite database (temporary, in memory). They have not been run against PostgreSQL. A manual run through `/docs` on 22 November with a local demo server returned 201 for a new dream and a journal entry, 200 for the lists, 204 for a delete and a correct weekly graph for the demo dream. That run was done by hand and is not part of the automated suite.
- `main.py` points `get_current_user_id` of the dream router to the real login through a dependency override (Riya's work). I have not tested the login flow independently. The weekly graph counts only the newest roadmap of a dream, because the Roadmap table has no active flag; the SRS says a dream has one roadmap, but the tables allow several.
- Under SRS FR-EV-01 a task can become completed only through accepted evidence. The default setting `EVIDENCE_REQUIRED=true` keeps that rule. The evidence service is not built yet, so with the default no task can reach "completed" and the weekly graph shows zero completed. For the two-week demo, `EVIDENCE_REQUIRED=false` lets a user mark tasks finished and reopen them without evidence. This is a deliberate deviation from FR-EV-01, for the demo only. Riya proposed the switch, and it is tested in `test_routers_db.py` (5 tests).
- Deleting a dream also deletes its roadmaps, milestones and tasks (SRS DR-02); this is tested for tasks in `test_routers_db.py`. Evidence, resources and quiz tables do not exist yet.
- `RoadmapResponse` requires `version` and `disclaimer`, but Ananya's Roadmap table has neither (DEF-012). Riya's roadmap router and `roadmap_service.py` are in `main` now, and I have not tested them.
- Not tested independently: `auth_service.py`, `roadmap_service.py`, `readiness_service.py`, `chat_flow_service.py`, and the auth, roadmap and chat routers (all in `main`; Riya wrote her own tests for them), and the frontend (I have not seen it in `main`).
- Every generated roadmap carries a general AI notice (tested). Whether roadmaps in medical, legal and other regulated fields get the specific notice of SRS FR-RG-08 has not been checked.
- Evidence verification, re-planning, reminders and resources were not part of this work. The file structure assigns them to Riya or marks them "Later".

## 6. Conclusion
The files covered here behaved as specified in the checks above. The
independent tests of Riya's code found DEF-005 to DEF-010; she fixed them and
the tests now pass. The Gemini client, roadmap generation, regeneration,
prompts and security tests found no defects. DEF-011 and DEF-013 (set-up
problems) are fixed. DEF-012 (the roadmap fields) is still open and needs a
team decision. The readiness score, the auth, roadmap and chat services and
routers, and the frontend still need independent testing.