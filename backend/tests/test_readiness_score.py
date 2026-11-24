"""
test_readiness_score.py - independent tests for Riya's readiness score.

PURPOSE
    readiness_service.py gives a learner a score from 0 to 100 that estimates
    progress towards a dream. The score is plain arithmetic (not AI). It adds
    four parts with fixed weights:
        tasks finished      50 %   (finished tasks / all tasks)
        on schedule         25 %   (of the tasks already due, how many are finished)
        weekly momentum     15 %   (in how many of the last 4 weeks more tasks were finished)
        reflection          10 %   (journal entries in the last 30 days, 4 or more = full)
    A part with no data yet is left out and the other weights are scaled up to
    100 %. The report also gives a level name and one "next step" sentence.
    These tests check the arithmetic and the rules from the outside. They also
    check the data loading of get_readiness() with FAKE repositories, so no
    database is used. Riya wrote 7 tests of her own (test_readiness.py); these
    tests are written separately and check other things.

WHAT IS TESTED
    1. The weights add up to 1.
    2. Level names change at exactly the right scores (10 boundary cases).
    3. An empty roadmap gives a "Not started" report.
    4. A full report with all four parts, worked out by hand (score 54).
    5. Perfect progress gives exactly 100.
    6. A task due today counts as due but is not overdue (score 44).
    7. Only the status "completed" counts as finished.
    8. Journal entries count up to 4 and no further.
    9. The next-step sentence: earliest overdue task first; low momentum next;
       then a low reflection; otherwise the earliest open task; exactly 0.5 is
       not low.
    10. The estimate note is always on the report.
    11. weeks_with_progress(): the 4-week window edges, unsorted input, and a
        week with fewer finished tasks is not progress.
    12. get_readiness() with fake repositories: another user's dream gives
        "not found"; the newest roadmap is used; the weekly snapshot is saved
        (or not saved); journal entries are counted only for this dream and
        within 30 days; today defaults to the real date.

NOTE ON PRIVATE NAMES
    _level is a private helper; it is tested directly because the level
    boundaries are an important rule.

HOW TO RUN
    cd backend
    pytest tests/test_readiness_score.py -v

WHO USES IT
    Sonali (M4 testing), reviewed by Riya (owner of readiness_service.py).
"""

import os  # to set dummy settings before the app loads

# dummy settings so the app can load in tests; never put a real key here
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only-0000")  # fake secret
os.environ.setdefault("GEMINI_API_KEY", "fake-key-not-real")                # fake AI key

from datetime import date, datetime, timedelta  # dates for tasks, snapshots and journal entries
from types import SimpleNamespace               # makes quick fake objects with named fields

import pytest  # the test tool

from app.core.exceptions import NotFoundError  # raised when a dream is not the user's
from app.services import readiness_service     # the module itself, so we can replace its repositories
from app.services.readiness_service import (   # the things we test
    BASE_WEIGHTS,       # the four fixed weights
    NOTE,               # the sentence that says the score is an estimate
    _level,             # turns a score into a level name (private, tested directly)
    compute_readiness,  # the pure formula (no database)
    get_readiness,      # loads the data, then calls the formula
    weeks_with_progress,  # counts the weeks of progress in the last 4 weeks
)

# "Today" is a Wednesday. Its Monday is 16 Nov 2026, so the 4-week window is
# the weeks starting 16 Nov, 9 Nov, 2 Nov and 26 Oct.
TODAY = date(2026, 11, 18)               # the day all formula tests pretend it is
THIS_WEEK = date(2026, 11, 16)           # Monday of this week
LAST_WEEK = date(2026, 11, 9)            # one week before
TWO_WEEKS_AGO = date(2026, 11, 2)        # two weeks before
THREE_WEEKS_AGO = date(2026, 10, 26)     # three weeks before (still inside the window)
FOUR_WEEKS_AGO = date(2026, 10, 19)      # four weeks before (outside the window)
NEXT_WEEK = date(2026, 11, 23)           # a week that has not started yet (outside the window)


# ---------- helpers: small builders so the tests stay short ----------

def task(status, days, title="A task"):
    # a fake task whose due date is `days` days after TODAY (negative = in the past)
    return SimpleNamespace(status=status, due_date=TODAY + timedelta(days=days), title=title)


def run(tasks, snapshots=(), journal=0):
    # runs the pure formula with fixed ids (dream 1, roadmap 7) and the fixed TODAY
    return compute_readiness(dream_id=1, roadmap_id=7, tasks=tasks, snapshots=list(snapshots),
                             journal_entries_30d=journal, today=TODAY)


def component(report, key):
    # finds one part of the report ("completion", "on_time", "momentum" or "reflection")
    return next(c for c in report.components if c.key == key)


# ---------- weights and levels ----------

def test_the_four_weights_add_up_to_one():
    assert sum(BASE_WEIGHTS.values()) == pytest.approx(1.0)   # 0.50 + 0.25 + 0.15 + 0.10


@pytest.mark.parametrize("score, level", [   # the same test runs once for each pair
    (0, "Just starting"), (19, "Just starting"),            # below 20
    (20, "Building foundations"), (44, "Building foundations"),  # 20 to 44
    (45, "Making progress"), (69, "Making progress"),       # 45 to 69
    (70, "Almost ready"), (89, "Almost ready"),             # 70 to 89
    (90, "Well prepared"), (100, "Well prepared"),          # 90 and above
])
def test_level_names_change_at_the_boundaries(score, level):
    assert _level(score) == level   # the name must match the score range


# ---------- the report ----------

def test_empty_roadmap_gives_a_not_started_report():
    report = run([])                                         # no tasks at all
    assert report.score == 0 and report.level == "Not started"   # nothing to measure yet
    assert report.components == []                           # so there are no parts
    assert (report.total_tasks, report.completed_tasks, report.overdue_tasks) == (0, 0, 0)  # all counts are zero
    assert report.dream_id == 1 and report.roadmap_id == 7   # the ids are passed through
    assert report.as_of == TODAY                             # the report says which day it is for
    assert report.next_step == "Generate your roadmap to start tracking readiness."  # the advice for a new user


def test_full_report_with_all_four_parts_is_worked_out_correctly():
    tasks = [
        task("completed", -10, "Done one"),         # finished, was due 10 days ago
        task("completed", -3, "Done two"),          # finished, was due 3 days ago
        task("pending", -2, "Learn SQL"),           # not finished, due 2 days ago: overdue
        task("pending", 5, "Mock interview"),       # not finished, due in 5 days
    ]
    snapshots = [(THIS_WEEK, 2), (LAST_WEEK, 1)]    # progress in two weeks (given in reverse order on purpose)
    report = run(tasks, snapshots, journal=2)       # and 2 journal entries
    # the parts, in the order the report lists them
    assert [c.key for c in report.components] == ["completion", "on_time", "momentum", "reflection"]
    # completion = 2 of 4 = 0.5; on time = 2 of the 3 tasks due = 0.667; momentum = 2 of 4 weeks = 0.5; reflection = 2 of 4 = 0.5
    assert [c.value for c in report.components] == pytest.approx([0.5, 0.667, 0.5, 0.5], abs=0.001)
    # all four parts are present, so the weights are the base weights
    assert [c.weight for c in report.components] == pytest.approx([0.5, 0.25, 0.15, 0.1], abs=0.001)
    # points = value x weight x 100
    assert [c.points for c in report.components] == pytest.approx([25.0, 16.7, 7.5, 5.0], abs=0.05)
    assert report.score == 54                       # 25 + 16.7 + 7.5 + 5 = 54.2, rounded
    assert report.level == "Making progress"        # 54 is in the 45 to 69 range
    assert (report.total_tasks, report.completed_tasks, report.overdue_tasks) == (4, 2, 1)  # the counts
    assert component(report, "completion").detail == "2 of 4 tasks finished"                 # the plain-language texts
    assert component(report, "on_time").detail == "2 of 3 tasks that were due are finished"
    assert component(report, "momentum").detail == "progress in 2 of the last 4 weeks"
    assert component(report, "reflection").detail == "2 journal entries in the last 30 days"
    assert report.next_step == "Catch up on 1 overdue task(s), starting with 'Learn SQL'."   # overdue comes first


def test_perfect_progress_scores_exactly_100():
    tasks = [task("completed", -d) for d in (10, 8, 5, 1)]   # four finished tasks, all already due
    snapshots = [(THREE_WEEKS_AGO, 1), (TWO_WEEKS_AGO, 2), (LAST_WEEK, 3), (THIS_WEEK, 4)]  # more done every week
    report = run(tasks, snapshots, journal=4)                # and 4 journal entries
    assert report.score == 100                               # 50 + 25 + 15 + 10
    assert report.level == "Well prepared"
    assert report.overdue_tasks == 0                         # nothing is late
    assert report.next_step == "You have finished every task. Review your roadmap or start a new dream."


def test_a_task_due_today_counts_as_due_but_is_not_overdue():
    tasks = [task("pending", 0, "Due today"), task("completed", 0, "Done today")]  # both are due today
    report = run(tasks)                                      # no snapshots, no journal entries
    assert report.overdue_tasks == 0                         # "overdue" means before today
    assert component(report, "on_time").value == pytest.approx(0.5, abs=0.001)  # 1 of the 2 due tasks is finished
    assert "momentum" not in [c.key for c in report.components]  # no snapshots, so no momentum part
    assert report.score == 44                                # 29.4 + 14.7 + 0 = 44.1, rounded
    assert report.level == "Building foundations"            # 44 is in the 20 to 44 range
    assert report.next_step == "Write a journal entry about what you learned this week."  # reflection is low


def test_only_the_status_completed_counts_as_finished():
    tasks = [task(status, 5) for status in ("pending", "submitted", "overdue", "completed")]  # one of each, all due later
    report = run(tasks)
    assert report.completed_tasks == 1                       # only "completed" counts
    assert report.total_tasks == 4
    assert component(report, "completion").value == pytest.approx(0.25, abs=0.001)  # 1 of 4


@pytest.mark.parametrize("journal, value", [   # entries and the value of the reflection part
    (0, 0.0), (1, 0.25), (2, 0.5), (4, 1.0), (10, 1.0),
])
def test_reflection_counts_up_to_four_entries_and_no_further(journal, value):
    report = run([task("pending", 7)], journal=journal)      # one task, due later
    part = component(report, "reflection")
    assert part.value == pytest.approx(value, abs=0.001)     # 4 or more entries give full marks
    assert part.detail == f"{journal} journal entries in the last 30 days"  # the text shows the real number


# ---------- the next-step sentence ----------

def test_next_step_starts_with_the_earliest_overdue_task():
    tasks = [
        task("pending", -2, "Later overdue"),       # overdue by 2 days
        task("pending", -9, "Earliest overdue"),    # overdue by 9 days
        task("pending", 6, "Future"),               # not due yet
    ]
    report = run(tasks)
    assert report.overdue_tasks == 2
    assert report.next_step == "Catch up on 2 overdue task(s), starting with 'Earliest overdue'."


def test_low_momentum_comes_before_low_reflection():
    tasks = [task("pending", 3, "Build API"), task("completed", -4, "Done early")]  # nothing is overdue
    report = run(tasks, [(THIS_WEEK, 1)], journal=0)         # progress in 1 of 4 weeks, and no journal entries
    assert report.next_step == "Finish at least one task every week. Next up: 'Build API'."  # momentum wins


def test_low_reflection_is_the_next_advice_when_momentum_is_fine():
    tasks = [task("pending", 3, "Build API"), task("completed", -4, "Done early")]
    report = run(tasks, [(LAST_WEEK, 1), (THIS_WEEK, 2)], journal=1)  # progress in 2 of 4 weeks, 1 journal entry
    assert report.next_step == "Write a journal entry about what you learned this week."


def test_next_step_points_to_the_earliest_open_task_not_the_first_in_the_list():
    tasks = [task("pending", 20, "Last"), task("pending", 4, "First"), task("completed", 1, "Done")]  # not in date order
    report = run(tasks, journal=4)                           # no snapshots, full reflection
    assert report.next_step == "Next up: 'First'."


def test_exactly_half_momentum_and_half_reflection_are_not_low():
    tasks = [task("pending", 3, "Build API"), task("completed", -4, "Done early")]
    report = run(tasks, [(LAST_WEEK, 1), (THIS_WEEK, 2)], journal=2)  # momentum 0.5 and reflection 0.5
    assert report.next_step == "Next up: 'Build API'."       # "low" means below 0.5


def test_every_report_carries_the_estimate_note():
    report = run([task("pending", 7)])
    assert report.note == NOTE                               # the same sentence as the constant
    assert "not a prediction" in report.note                 # it says the score is not a prediction


# ---------- weeks_with_progress ----------

@pytest.mark.parametrize("snapshots, expected", [   # the same test runs once for each pair
    ([(THIS_WEEK, 1)], 1),           # this week counts
    ([(THREE_WEEKS_AGO, 1)], 1),     # three weeks ago is the oldest week inside the window
    ([(FOUR_WEEKS_AGO, 1)], 0),      # four weeks ago is outside the window
    ([(NEXT_WEEK, 1)], 0),           # a week in the future is outside the window
    ([(THIS_WEEK, 0)], 0),           # nothing finished is not progress
    ([], 0),                         # no snapshots at all
])
def test_the_window_covers_the_last_four_weeks_only(snapshots, expected):
    assert weeks_with_progress(snapshots, TODAY) == expected


def test_snapshots_are_sorted_before_they_are_compared():
    # in date order this is 1 then 2 (two weeks of progress); unsorted it would look like 2 then 1
    assert weeks_with_progress([(THIS_WEEK, 2), (LAST_WEEK, 1)], TODAY) == 2


def test_a_week_with_fewer_finished_tasks_than_before_is_not_progress():
    # two weeks ago 3 tasks were finished; last week only 1 (a task was reopened)
    assert weeks_with_progress([(TWO_WEEKS_AGO, 3), (LAST_WEEK, 1)], TODAY) == 1  # only the first week counts


# ---------- get_readiness with fake repositories (no database) ----------

OWNER = (5, 1)   # the dream that exists: dream id 5 belongs to user id 1


def fake_repos(monkeypatch, roadmaps=(), tasks_by_roadmap=None, snapshots=(), entries=()):
    # replaces the five repositories inside readiness_service with fakes; returns the list of saved snapshots
    tasks_by_roadmap = tasks_by_roadmap or {}   # roadmap id -> its tasks
    saved = []                                  # every snapshot that get_readiness saves

    def save_weekly_snapshot(db, user_id, dream_id, week_start, completed, total):
        saved.append((user_id, dream_id, week_start, completed, total))  # remember what was saved

    monkeypatch.setattr(readiness_service, "dream_repository", SimpleNamespace(
        # the dream exists only for its owner (a dream of another user gives None)
        get_dream=lambda db, dream_id, user_id: SimpleNamespace(id=dream_id) if (dream_id, user_id) == OWNER else None))
    monkeypatch.setattr(readiness_service, "roadmap_repository", SimpleNamespace(
        list_roadmaps=lambda db, dream_id: list(roadmaps)))              # newest first, like the real one
    monkeypatch.setattr(readiness_service, "task_repository", SimpleNamespace(
        list_tasks_for_roadmap=lambda db, roadmap_id: list(tasks_by_roadmap.get(roadmap_id, []))))
    monkeypatch.setattr(readiness_service, "analytics_repository", SimpleNamespace(
        save_weekly_snapshot=save_weekly_snapshot,
        list_snapshots=lambda db, user_id, dream_id: list(snapshots)))
    monkeypatch.setattr(readiness_service, "journal_repository", SimpleNamespace(
        list_entries=lambda db, user_id: list(entries)))
    return saved


def test_an_unknown_dream_gives_not_found_and_saves_nothing(monkeypatch):
    saved = fake_repos(monkeypatch)                          # dream 5 exists for user 1 only
    with pytest.raises(NotFoundError):
        get_readiness(None, 1, 99, today=TODAY)              # dream 99 does not exist
    assert saved == []                                       # nothing was written


def test_another_users_dream_gives_not_found(monkeypatch):
    fake_repos(monkeypatch)
    with pytest.raises(NotFoundError):
        get_readiness(None, 2, 5, today=TODAY)               # dream 5 belongs to user 1, not user 2


def test_a_dream_without_a_roadmap_gives_an_empty_report(monkeypatch):
    saved = fake_repos(monkeypatch, roadmaps=[])             # no roadmap yet
    report = get_readiness(None, 1, 5, today=TODAY)
    assert report.roadmap_id is None                         # there is no roadmap id
    assert report.level == "Not started" and report.total_tasks == 0
    assert saved == []                                       # and no snapshot is saved


def test_the_newest_roadmap_is_used(monkeypatch):
    fake_repos(monkeypatch,
               roadmaps=[SimpleNamespace(id=2), SimpleNamespace(id=1)],   # newest first: roadmap 2 is the current one
               tasks_by_roadmap={2: [task("completed", -1), task("pending", 5)],     # 2 tasks
                                 1: [task("pending", 5) for _ in range(5)]})         # 5 tasks of an older roadmap
    report = get_readiness(None, 1, 5, today=TODAY)
    assert report.roadmap_id == 2                            # the newest roadmap
    assert report.total_tasks == 2                           # only its tasks are counted
    assert report.completed_tasks == 1


def test_this_weeks_snapshot_is_saved_with_the_finished_and_total_counts(monkeypatch):
    saved = fake_repos(monkeypatch, roadmaps=[SimpleNamespace(id=2)],
                       tasks_by_roadmap={2: [task("completed", -1), task("pending", 5)]})
    get_readiness(None, 1, 5, today=TODAY)
    assert saved == [(1, 5, THIS_WEEK, 1, 2)]                # user 1, dream 5, Monday 16 Nov, 1 finished, 2 in total


def test_no_snapshot_is_saved_when_record_snapshot_is_false(monkeypatch):
    saved = fake_repos(monkeypatch, roadmaps=[SimpleNamespace(id=2)],
                       tasks_by_roadmap={2: [task("completed", -1), task("pending", 5)]})
    get_readiness(None, 1, 5, today=TODAY, record_snapshot=False)
    assert saved == []                                       #