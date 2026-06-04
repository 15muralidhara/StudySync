"""
Automated pytest suite for the NLP entity extractor.

Runs against the ground-truth eval set in eval_set.py.
No server required — tests call extract_entities() directly.

Cases with a "known_failure" key are marked xfail — they document
real bugs without causing the suite to go red.
"""

import pytest
from nlp.nlp import extract_entities
from tests.eval_set import EVAL_SET, ANY_DATE, NO_DATE


# ── Helpers ──────────────────────────────────────────────────────────────────

def participants_match(actual: list, expected: list) -> bool:
    """All expected names appear in actual (case-insensitive, order-insensitive)."""
    actual_lower = [p.lower() for p in actual]
    return all(e.lower() in actual_lower for e in expected)


def locations_match(actual: list, expected: list) -> bool:
    """All expected locations appear in actual (case-insensitive substring match)."""
    actual_lower = [l.lower() for l in actual]
    for exp in expected:
        if not any(exp.lower() in a for a in actual_lower):
            return False
    return True


def is_known_failure(case: dict) -> bool:
    return "known_failure" in case


# ── Parametrised tests ────────────────────────────────────────────────────────

@pytest.mark.parametrize("case", EVAL_SET, ids=[c["id"] for c in EVAL_SET])
def test_task_is_extracted(case):
    if is_known_failure(case):
        pytest.xfail(case["known_failure"])
    result = extract_entities(case["text"])
    assert result["task"] is not None and result["task"].strip() != "", (
        f"[{case['id']}] Expected a task to be extracted from: '{case['text']}'"
    )


@pytest.mark.parametrize("case", EVAL_SET, ids=[c["id"] for c in EVAL_SET])
def test_participants(case):
    if is_known_failure(case):
        pytest.xfail(case["known_failure"])
    expected = case["expected"]["participants"]
    result = extract_entities(case["text"])
    assert participants_match(result["participants"], expected), (
        f"[{case['id']}] Expected participants {expected}, got {result['participants']}\n"
        f"  Input: '{case['text']}'"
    )


@pytest.mark.parametrize("case", EVAL_SET, ids=[c["id"] for c in EVAL_SET])
def test_date(case):
    if is_known_failure(case):
        pytest.xfail(case["known_failure"])
    expected_date = case["expected"]["date"]
    result = extract_entities(case["text"])
    actual_date = result["date"]

    if expected_date == ANY_DATE:
        assert actual_date is not None, (
            f"[{case['id']}] Expected some date to be extracted, got None\n"
            f"  Input: '{case['text']}'"
        )
    elif expected_date == NO_DATE:
        assert actual_date is None, (
            f"[{case['id']}] Expected no date, got '{actual_date}'\n"
            f"  Input: '{case['text']}'"
        )
    else:
        assert actual_date == expected_date, (
            f"[{case['id']}] Expected date '{expected_date}', got '{actual_date}'\n"
            f"  Input: '{case['text']}'"
        )


@pytest.mark.parametrize("case", EVAL_SET, ids=[c["id"] for c in EVAL_SET])
def test_time(case):
    if is_known_failure(case):
        pytest.xfail(case["known_failure"])
    expected_time = case["expected"]["time"]
    result = extract_entities(case["text"])
    assert result["time"] == expected_time, (
        f"[{case['id']}] Expected time '{expected_time}', got '{result['time']}'\n"
        f"  Input: '{case['text']}'"
    )


@pytest.mark.parametrize("case", EVAL_SET, ids=[c["id"] for c in EVAL_SET])
def test_end_time(case):
    if is_known_failure(case):
        pytest.xfail(case["known_failure"])
    expected_end = case["expected"]["end_time"]
    result = extract_entities(case["text"])
    assert result["end_time"] == expected_end, (
        f"[{case['id']}] Expected end_time '{expected_end}', got '{result['end_time']}'\n"
        f"  Input: '{case['text']}'"
    )


@pytest.mark.parametrize("case", EVAL_SET, ids=[c["id"] for c in EVAL_SET])
def test_locations(case):
    if is_known_failure(case):
        pytest.xfail(case["known_failure"])
    expected = case["expected"]["locations"]
    result = extract_entities(case["text"])
    assert locations_match(result["locations"], expected), (
        f"[{case['id']}] Expected locations {expected}, got {result['locations']}\n"
        f"  Input: '{case['text']}'"
    )


# ── Confidence score tests ────────────────────────────────────────────────────

@pytest.mark.parametrize("case", EVAL_SET, ids=[c["id"] for c in EVAL_SET])
def test_confidence_scores(case):
    """Assert min/max confidence thresholds where specified in the eval set."""
    result = extract_entities(case["text"])
    conf = result["field_confidence"]

    if "min_participant_confidence" in case["expected"]:
        threshold = case["expected"]["min_participant_confidence"]
        assert conf["participants"] >= threshold, (
            f"[{case['id']}] Expected participant confidence >= {threshold}, got {conf['participants']:.2f}\n"
            f"  Input: '{case['text']}'"
        )

    if "min_task_confidence" in case["expected"]:
        threshold = case["expected"]["min_task_confidence"]
        assert conf["task"] >= threshold, (
            f"[{case['id']}] Expected task confidence >= {threshold}, got {conf['task']:.2f}\n"
            f"  Input: '{case['text']}'"
        )

    if "max_task_confidence" in case["expected"]:
        threshold = case["expected"]["max_task_confidence"]
        assert conf["task"] <= threshold, (
            f"[{case['id']}] Expected task confidence <= {threshold}, got {conf['task']:.2f}\n"
            f"  Input: '{case['text']}'"
        )


# ── Precision / Recall summary (collected at end of session) ──────────────────

class EvalMetrics:
    """Accumulates TP/FP/FN counts across the eval set for a single field."""

    def __init__(self):
        self.tp = self.fp = self.fn = 0

    def update(self, actual: list, expected: list):
        actual_s = {s.lower() for s in actual}
        expected_s = {s.lower() for s in expected}
        self.tp += len(actual_s & expected_s)
        self.fp += len(actual_s - expected_s)
        self.fn += len(expected_s - actual_s)

    @property
    def precision(self):
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self):
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self):
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def test_precision_recall_report(capsys):
    """
    Runs the full eval set and prints a precision/recall/F1 summary per field.
    This test always passes — it is a measurement, not a gate.
    """
    participant_metrics = EvalMetrics()
    location_metrics = EvalMetrics()

    time_correct = time_total = 0
    end_time_correct = end_time_total = 0
    date_correct = date_total = 0
    task_correct = task_total = 0

    for case in EVAL_SET:
        result = extract_entities(case["text"])
        exp = case["expected"]

        # Participants
        participant_metrics.update(result["participants"], exp["participants"])

        # Locations
        location_metrics.update(result["locations"], exp["locations"])

        # Time (exact match)
        time_total += 1
        if result["time"] == exp["time"]:
            time_correct += 1

        # End time (exact match)
        end_time_total += 1
        if result["end_time"] == exp["end_time"]:
            end_time_correct += 1

        # Date
        date_total += 1
        ed = exp["date"]
        if ed == ANY_DATE and result["date"] is not None:
            date_correct += 1
        elif ed == NO_DATE and result["date"] is None:
            date_correct += 1
        elif result["date"] == ed:
            date_correct += 1

        # Task presence
        task_total += 1
        if result["task"] and result["task"].strip():
            task_correct += 1

    with capsys.disabled():
        print("\n")
        print("=" * 65)
        print("  StudySync NLP — Evaluation Report")
        print(f"  Eval set size: {len(EVAL_SET)} inputs")
        print("=" * 65)
        print(f"  {'Field':<20} {'Accuracy/P':<12} {'R':<8} {'F1/Score'}")
        print("-" * 65)
        print(f"  {'Task':<20} {task_correct/task_total:.0%}  ({task_correct}/{task_total})")
        print(f"  {'Date':<20} {date_correct/date_total:.0%}  ({date_correct}/{date_total})")
        print(f"  {'Time':<20} {time_correct/time_total:.0%}  ({time_correct}/{time_total})")
        print(f"  {'End Time':<20} {end_time_correct/end_time_total:.0%}  ({end_time_correct}/{end_time_total})")
        print(f"  {'Participants':<20} P={participant_metrics.precision:.0%}         R={participant_metrics.recall:.0%}     F1={participant_metrics.f1:.0%}")
        print(f"  {'Locations':<20} P={location_metrics.precision:.0%}         R={location_metrics.recall:.0%}     F1={location_metrics.f1:.0%}")
        print("=" * 65)
