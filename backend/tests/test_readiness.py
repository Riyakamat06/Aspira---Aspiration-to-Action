"""Pure unit tests for the readiness formula (no database)."""
import os, sys
os.environ.setdefault("SECRET_KEY", "x" * 40); os.environ.setdefault("GEMINI_API_KEY", "k" * 20)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import date, timedelta
from types import SimpleNamespace as T
from app.services.readiness_service import compute_readiness, weeks_with_progress

TODAY = date(2026, 11, 18)  # a Wednesday; its Monday is 2026-11-16

def task(status, days, title="t"): return T(status=status, due_date=TODAY + timedelta(days=days), title=title)
def run(tasks, snaps=(), journal=0): return compute_readiness(dream_id=1, roadmap_id=1, tasks=tasks, snapshots=list(snaps), journal_entries_30d=journal, today=TODAY)

def test_empty_roadmap():
    r = run([]); assert r.score == 0 and r.level == "Not started" and r.components == []

def test_fresh_roadmap_is_not_punished_for_unmeasurable_parts():
    r = run([task("pending", 7), task("pending", 14)])
    assert {c.key for c in r.components} == {"completion", "reflection"}
    assert abs(sum(c.weight for c in r.components) - 1) < 0.01 and r.score == 0

def test_everything_done_scores_high():
    tasks = [task("completed", -3), task("completed", -10), task("completed", 5)]
    snaps = [(date(2026, 11, 16), 3), (date(2026, 11, 9), 1)]
    r = run(tasks, snaps, journal=4)
    assert r.score >= 90 and r.level == "Well prepared" and "finished every task" in r.next_step

def test_overdue_drives_next_step_and_lowers_on_time():
    r = run([task("pending", -5, "Learn SQL"), task("completed", -2), task("pending", 9)])
    assert r.overdue_tasks == 1 and "Learn SQL" in r.next_step
    on_time = next(c for c in r.components if c.key == "on_time")
    assert on_time.value == 0.5

def test_submitted_does_not_count_as_finished():
    r = run([task("submitted", 3), task("completed", 3)])
    assert r.completed_tasks == 1

def test_momentum_window():
    snaps = [(date(2026, 10, 26), 1), (date(2026, 11, 2), 1), (date(2026, 11, 9), 3), (date(2026, 11, 16), 4)]
    assert weeks_with_progress(snaps, TODAY) == 3   # weeks of Nov 16, Nov 9 and Oct 26 gained; Nov 2 did not
    assert weeks_with_progress([], TODAY) == 0

def test_score_bounds():
    for status in ("pending", "completed", "overdue"):
        r = run([task(status, -30)] * 5, [(date(2026, 11, 16), 5)], journal=99)
        assert 0 <= r.score <= 100
