"""
test_disclaimer_service.py - independent tests for Riya's responsible-AI notices.

PURPOSE
    disclaimer_service.py reads the AI's answer and adds short warning notices
    when the answer talks about sensitive things: salary, guarantees, visas and
    legal matters, health, or investing. The notices are returned in a separate
    list (the answer text itself is never changed) so the website can style them.
    These tests check that behaviour from the outside. No AI is called.

WHAT IS TESTED
    1. detect_topics() finds the right topic for 7 example sentences.
    2. The guarantee notice says that outcomes cannot be guaranteed.
    3. The answer text is returned exactly as it came in.
    4. Plain advice and empty text get no notice.
    5. A word repeated many times gives only ONE notice for that topic.
    6. An answer with two topics gets two notices.
    7. roadmap_notice() and refusal() return the expected fixed messages.

KNOWN FINDINGS (marked xfail)
    xfail means "expected to fail": the test describes the CORRECT behaviour,
    the code does not do it yet, and pytest reports XFAIL without breaking the run.
    Each finding is logged in docs/defect_log.md.
      - The word "package" (software package) triggers the salary notice.
      - "per month" (study hours) triggers the salary notice.
      - "invest time" triggers the "not financial advice" notice.
      - Answers about becoming a lawyer or a doctor get no notice
        (SRS section 3.6 and NFR-12).

HOW TO RUN
    cd backend
    pytest tests/test_disclaimer_service.py -v

WHO USES IT
    Sonali (M4 testing), reviewed by Riya (owner of disclaimer_service.py).
"""

import pytest  # the test tool; used here for parametrize and xfail

from app.services.disclaimer_service import (  # the things we test
    apply_disclaimers,  # returns (answer, list of notices)
    detect_topics,      # returns the names of the topics found, like ["salary"]
    refusal,            # the fixed message for non-career questions
    roadmap_notice,     # the fixed notice shown on every roadmap
)


@pytest.mark.parametrize("text, topic", [  # the same test runs once for each pair below
    ("Typical salary for freshers is 6 LPA.", "salary"),                  # the words salary and LPA
    ("Expect ₹6 lakh to start.", "salary"),                               # a money symbol with a number
    ("You will definitely get a job after this course.", "guarantee"),    # a promise
    ("We guarantee you a placement.", "guarantee"),                       # the word guarantee
    ("You may need a work visa to take that job.", "legal"),              # a visa
    ("Burnout and anxiety are common during exam season.", "health"),     # health words
    ("Learn about mutual funds and stocks.", "finance"),                  # investing words
])
def test_topic_is_detected(text, topic):
    # exactly this one topic must be found, and no other
    assert detect_topics(text) == [topic]


def test_guarantee_notice_says_outcomes_cannot_be_guaranteed():
    _, notices = apply_disclaimers("You will definitely get a job after this course.")  # a promise
    assert len(notices) == 1                       # one topic, so one notice
    assert "guaranteed" in notices[0]              # the notice explains that nothing is guaranteed


def test_answer_text_is_not_changed():
    answer = "Typical salary for freshers is 6 LPA."  # an answer that will get a notice
    text, _ = apply_disclaimers(answer)               # the first value returned is the text
    assert text == answer                             # it must come back exactly as it went in


def test_plain_advice_gets_no_notice():
    _, notices = apply_disclaimers("Practise one DSA problem every day.")  # nothing sensitive
    assert notices == []                                                  # so the list is empty


def test_empty_text_gets_no_notice():
    text, notices = apply_disclaimers("")  # nothing to check
    assert text == ""                      # the text stays empty
    assert notices == []                   # and there are no notices


def test_repeated_keyword_gives_only_one_notice():
    _, notices = apply_disclaimers("salary salary salary salary")  # one topic, said four times
    assert len(notices) == 1                                        # still one notice, not four


def test_two_topics_give_two_notices():
    _, notices = apply_disclaimers("You will definitely get a 6 LPA package.")  # promise + salary
    assert len(notices) == 2                                                   # one notice for each topic


def test_roadmap_notice_says_it_is_ai_generated():
    assert "AI-generated" in roadmap_notice()  # the roadmap warning names the AI


def test_refusal_message_points_back_to_careers():
    message = refusal()                # the message for non-career questions
    assert message.strip() != ""       # it is not empty
    assert "career" in message         # and it steers the user back to careers


def test_software_package_does_not_trigger_salary_notice():
    _, notices = apply_disclaimers("Install the pandas package first.")  # about software, not pay
    assert notices == []                                                 # correct: no notice


def test_hours_per_month_does_not_trigger_salary_notice():
    _, notices = apply_disclaimers("Practise 5 hours per month.")  # about study time, not pay
    assert notices == []                                           # correct: no notice


def test_invest_time_does_not_trigger_finance_notice():
    _, notices = apply_disclaimers("Invest time in practising DSA daily.")  # about time, not money
    assert notices == []                                                    # correct: no notice


@pytest.mark.parametrize("answer", [
    "To become a lawyer, complete an LLB and enrol with the Bar Council.",  # a legal career
    "To become a doctor, clear NEET and complete MBBS.",                    # a medical career
])
def test_regulated_career_answer_gets_a_notice(answer):
    _, notices = apply_disclaimers(answer)  # check the answer
    assert len(notices) >= 1                # correct behaviour: at least one notice