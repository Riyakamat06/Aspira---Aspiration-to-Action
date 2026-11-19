"""
test_roadmap_prompts.py - independent tests for Riya's AI prompt builders.

PURPOSE
    roadmap_prompts.py (app/prompts/roadmap_prompts.py) builds the text that is
    sent to the AI: the first roadmap request, the "revise my roadmap" request
    and the note that asks the AI to fix problems in its own plan. If a field
    is missing from this text, the AI plans without it and the learner gets a
    wrong roadmap, so these tests check that every piece of information
    arrives in the text. No AI and no network are used.

WHAT IS TESTED
    1. The roadmap prompt contains every answer of the learner.
    2. Empty skills and empty extra context are replaced by clear words.
    3. The revision prompt starts with the normal prompt and adds the
       remaining weeks and hours.
    4. Previous and finished task titles are listed one per line; empty lists
       show "(none)"; only the first 80 titles of a list are used.
    5. Feedback is included when given, and a default sentence is used when not.
    6. The repair note lists every problem.
    7. The revision system prompt extends the roadmap system prompt.

NOT TESTED HERE
    The full wording of ROADMAP_SYSTEM (the long instruction text). We check
    only the parts that matter for regeneration.

HOW TO RUN
    cd backend
    pytest tests/test_roadmap_prompts.py -v

WHO USES IT
    Sonali (M4 testing), reviewed by Riya (owner of roadmap_prompts.py).
"""

import os  # to set dummy settings before the app loads

# dummy settings so the app can load in tests; never put a real key here
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only-0000")  # fake secret
os.environ.setdefault("GEMINI_API_KEY", "fake-key-not-real")                # fake AI key

from app.prompts.roadmap_prompts import (  # the things we test
    REGEN_SYSTEM,           # the AI's instructions when it revises a roadmap
    ROADMAP_SYSTEM,         # the AI's instructions when it creates a roadmap
    build_regen_prompt,     # builds the "revise my roadmap" text
    build_repair_note,      # builds the "fix these problems" note
    build_roadmap_prompt,   # builds the first roadmap request
)


def roadmap_prompt(**changes):
    # a normal roadmap prompt; a test can change any field it cares about
    fields = dict(career="Backend Developer", level="beginner", skills="Python",
                  hours_per_week=10, timeline_months=3, total_weeks=13,
                  total_hours=130, learning_style="mixed", extra="Final year BCA")
    fields.update(changes)                     # apply the changes of this test
    return build_roadmap_prompt(**fields)      # build the text


def regen_prompt(**changes):
    # a normal revision prompt; a test can change any field it cares about
    fields = dict(base="BASE PROMPT", previous_titles=["Task 1", "Task 2"],
                  completed_titles=["Task 1"], feedback="", remaining_weeks=11,
                  remaining_hours=110)
    fields.update(changes)                     # apply the changes of this test
    return build_regen_prompt(**fields)        # build the text


# ---------- the first roadmap request ----------

def test_roadmap_prompt_contains_every_answer():
    text = roadmap_prompt()                                  # build it
    assert "target_career: Backend Developer" in text        # the goal
    assert "current_level: beginner" in text                 # the level
    assert "known_skills: Python" in text                    # what the learner knows
    assert "hours_per_week: 10" in text                      # time per week
    assert "timeline_months: 3" in text                      # months available
    assert "total_weeks: 13" in text                         # weeks available
    assert "total_hours_available: 130" in text              # hours available
    assert "learning_style: mixed" in text                   # how the learner likes to learn
    assert "extra_context: Final year BCA" in text           # the extra note


def test_empty_skills_and_extra_context_get_clear_words():
    text = roadmap_prompt(skills="", extra="")               # nothing was answered
    assert "known_skills: none stated" in text               # the AI is told there are no skills
    assert "extra_context: none" in text                     # and no extra note


# ---------- the revision request ----------

def test_revision_prompt_starts_with_the_base_prompt():
    text = regen_prompt()
    assert text.startswith("BASE PROMPT")                    # the normal prompt comes first
    assert "--- REVISION CONTEXT ---" in text                # then the revision part


def test_revision_prompt_has_the_remaining_weeks_and_hours():
    text = regen_prompt(remaining_weeks=11, remaining_hours=110)
    assert "remaining_weeks: 11" in text                     # weeks left
    assert "remaining_hours_available: 110" in text          # hours left


def test_previous_and_finished_titles_are_listed_one_per_line():
    text = regen_prompt()
    expected = ("previous_plan_task_titles:\n- Task 1\n- Task 2\n"  # every old title on its own line
                "completed_tasks:\n- Task 1\n"                      # then the finished ones
                "learner_feedback:")                                # then the feedback line
    assert expected in text                                  # the order and the layout are right


def test_empty_title_lists_show_none():
    text = regen_prompt(previous_titles=[], completed_titles=[])
    assert text.count("- (none)") == 2                       # once for the old plan, once for the finished tasks


def test_only_the_first_80_titles_of_a_list_are_used():
    titles = [f"T{i}" for i in range(100)]                   # 100 titles: T0 to T99
    lines = regen_prompt(previous_titles=titles, completed_titles=[]).splitlines()
    assert "- T79" in lines                                  # the 80th title is there
    assert "- T80" not in lines                              # the 81st is not
    assert len([line for line in lines if line.startswith("- T")]) == 80  # exactly 80 title lines


def test_feedback_is_included_when_given():
    text = regen_prompt(feedback="<user_input>more projects</user_input>")
    assert "learner_feedback: <user_input>more projects</user_input>" in text  # the feedback is there
    assert "no specific feedback" not in text                # and the default sentence is not used


def test_default_sentence_is_used_when_there_is_no_feedback():
    text = regen_prompt(feedback="")
    assert "no specific feedback" in text                    # the AI is told to improve the plan by itself


# ---------- the repair note ----------

def test_repair_note_lists_every_problem():
    problems = ["Provide at least 2 phases.", "Provide at least 6 distinct tasks (got 3)."]
    note = build_repair_note(problems)
    lines = note.splitlines()                                # one text line per line
    assert "fix them all" in note                            # the AI is asked to fix everything
    assert "- Provide at least 2 phases." in lines           # the first problem is listed
    assert "- Provide at least 6 distinct tasks (got 3)." in lines  # and the second


# ---------- the system prompts ----------

def test_revision_system_prompt_extends_the_roadmap_system_prompt():
    assert "Aspira" in ROADMAP_SYSTEM                        # the normal prompt names the product
    assert REGEN_SYSTEM.startswith(ROADMAP_SYSTEM)           # the revision prompt keeps all of it
    assert "REVISING" in REGEN_SYSTEM                        # and says this is a revision
    assert "completed_tasks" in REGEN_SYSTEM                 # and points to the finished tasks
    assert "never repeat" in REGEN_SYSTEM                    # and says not to repeat them