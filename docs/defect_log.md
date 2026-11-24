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

| ID | Date | Found by | File | Description | Severity | Status | Fixed in | Re-tested by |
|---|---|---|---|---|---|---|---|---|
| DEF-001 | 2026-11-15 | Sonali | `app/schemas/task_schema.py` | The file was committed empty, so `TaskCreate` could not be imported | High | Fixed | Commit "Add dream and task schema content" | |
| DEF-002 | 2026-11-15 | Sonali | `app/schemas/dream_schema.py` | The file was committed empty, so `DreamCreate` could not be imported | High | Fixed | Commit "Add dream and task schema content" | |
| DEF-003 | 2026-11-15 | Sonali | `constants.py`, `task_service.py` | The status word "missed" did not match the SRS, which says "overdue" | Medium | Fixed | Commit "Use SRS status word overdue" | |
| DEF-004 | 2026-11-19 | Sonali | `schemas/chat_schema.py` (Sonali), `config.py` (Riya) | Chat message limit was 2000 in the schema but 1500 in the settings, so a 1501 to 2000 character message passed one check and failed the other | Medium | Fixed | Branch `sonali/m4-tests` (schema changed to 1500) | |
| DEF-005 | 2026-11-19 | Sonali | `services/scope_guard.py` (Riya) | A normal sentence with "new instructions:" is blocked as an injection. Test: `test_normal_sentence_with_new_instructions_is_allowed` | Low | Fixed | Riya's PR `riya/m2-final` | Sonali, 2026-11-25: `test_normal_sentence_with_new_instructions_is_allowed` passes |
| DEF-006 | 2026-11-19 | Sonali | `services/scope_guard.py` (Riya) | A normal sentence with "you are now" is blocked as an injection. Test: `test_normal_sentence_with_you_are_now_is_allowed` | Low | Fixed | Riya's PR `riya/m2-final` | Sonali, 2026-11-25: `test_normal_sentence_with_you_are_now_is_allowed` passes |
| DEF-007 | 2026-11-19 | Sonali | `services/disclaimer_service.py` (Riya) | The word "package" (a software package) triggers the salary notice | Low | Fixed | Riya's PR `riya/m2-final` | Sonali, 2026-11-25: `test_software_package_does_not_trigger_salary_notice` passes |
| DEF-008 | 2026-11-19 | Sonali | `services/disclaimer_service.py` (Riya) | "per month" (for example study hours) triggers the salary notice | Low | Fixed | Riya's PR `riya/m2-final` | Sonali, 2026-11-25: `test_hours_per_month_does_not_trigger_salary_notice` passes |
| DEF-009 | 2026-11-19 | Sonali | `services/disclaimer_service.py` (Riya) | "Invest time" triggers the "not financial advice" notice | Low | Fixed | Riya's PR `riya/m2-final` | Sonali, 2026-11-25: `test_invest_time_does_not_trigger_finance_notice` passes |
| DEF-010 | 2026-11-19 | Sonali | `services/disclaimer_service.py` (Riya) | Answers about becoming a lawyer or a doctor get no notice from `apply_disclaimers`. SRS section 3.6 and NFR-12 ask for the disclaimer on medical and legal chat answers. To confirm with Riya: the chat prompt may add it | Medium | Fixed | Riya's PR `riya/m2-final` | Sonali, 2026-11-25: `test_regulated_career_answer_gets_a_notice` passes for lawyer and doctor |
| DEF-011 | 2026-11-20 | Sonali | `backend/.env.example` | The file is empty, and the app stops at start without `SECRET_KEY` (at least 32 characters) and `GEMINI_API_KEY`. The setup guide has step 3b, but the template is still missing | Medium | Fixed | Riya's PR `riya/m2-final` | Sonali, 2026-11-25: the file now lists the 8 settings; no real key seen |
| DEF-012 | 2026-11-20 | Sonali | `app/schemas/roadmap_schema.py`, `app/models/roadmap.py` | `RoadmapResponse` requires `version` and `disclaimer`, but Ananya's Roadmap table has neither (SRS section 5.1 names them), so roadmap endpoints returning her objects would fail validation | Medium | Open (team decision) | | |
| DEF-013 | 2026-11-22 | Sonali | server start-up (`main.py`, models package) | POST /dreams returned 500 (NoReferencedTableError: `dreams.user_id` could not find table `users`) when the server loaded only the routers, because the model files were not imported | Medium | Fixed | `main.py` now calls `init_db` at start-up | Sonali, 2026-11-25: after importing `app.main`, all 8 tables are registered |
