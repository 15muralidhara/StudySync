"""
Ground-truth labelled evaluation set for the NLP entity extractor.

Each entry has:
  - text: the raw input string
  - expected: dict of ground-truth values (None means "should not be extracted")
  - id: short label for reporting

Fields checked:
  task        - not None (we check presence, not exact string, since it varies)
  participants - list of expected names (order-insensitive subset check)
  date        - exact YYYY-MM-DD string OR a special marker (see below)
  time        - exact HH:MM string
  end_time    - exact HH:MM string or None
  locations   - list of expected location strings (subset check)

Date markers (used when date is relative and changes daily):
  ANY_DATE    - some date was extracted, we don't care which
  NO_DATE     - no date should be extracted
"""

ANY_DATE = "__ANY_DATE__"
NO_DATE = "__NO_DATE__"

EVAL_SET = [
    # ── From input.json ──────────────────────────────────────────────────────
    {
        "id": "input_01",
        "text": "dentist appointment on Thursday at 3pm",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": "15:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "input_02",
        "text": "pick up groceries on Saturday morning",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": None,
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "input_03",
        "text": "call Ann regarding project update on Sunday at noon",
        "expected": {
            "task": True,
            "participants": ["Ann"],
            "date": ANY_DATE,
            "time": "12:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "input_04",
        "text": "gym workout at 6am tomorrow",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": "06:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "input_05",
        "text": "plan birthday party for friend on next Friday",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": None,
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "input_06",
        "text": "complete online course module by midnight",
        "expected": {
            "task": True,
            "participants": [],
            "date": NO_DATE,
            "time": "00:00",
            "end_time": None,
            "locations": [],
        },
    },

    # ── Standard examples from test_simple_nlp.py ────────────────────────────
    {
        "id": "std_01",
        "text": "Meeting with John tomorrow at 2pm",
        "expected": {
            "task": True,
            "participants": ["John"],
            "date": ANY_DATE,
            "time": "14:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "std_02",
        "text": "Dentist appointment on Friday at 3:30pm",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": "15:30",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "std_03",
        "text": "Call mom on Sunday evening",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": None,
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "std_04",
        "text": "Coffee with Sarah at Starbucks on Wednesday morning",
        "expected": {
            "task": True,
            "participants": ["Sarah"],
            "date": ANY_DATE,
            "time": None,
            "end_time": None,
            "locations": ["Starbucks"],
        },
    },
    {
        "id": "std_05",
        "text": "Meet John and Ashley at the conference room at 3PM",
        "expected": {
            "task": True,
            "participants": ["John", "Ashley"],
            "date": NO_DATE,
            "time": "15:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "std_06",
        "text": "Lunch with Tim and Sarah at Cafe Nero at noon",
        "expected": {
            "task": True,
            "participants": ["Tim", "Sarah"],
            "date": NO_DATE,
            "time": "12:00",
            "end_time": None,
            "locations": ["Cafe Nero"],
        },
    },

    # ── Time range tests (T1/T2/T3 from test_simple_nlp.py) ──────────────────
    {
        "id": "time_range_T1",
        "text": "Drive to Chicago with Ashley from 10AM to 4PM",
        "expected": {
            "task": True,
            "participants": ["Ashley"],
            "date": NO_DATE,
            "time": "10:00",
            "end_time": "16:00",
            "locations": ["Chicago"],
        },
    },
    {
        "id": "time_range_T2",
        "text": "Meeting from 2pm to 5pm",
        "expected": {
            "task": True,
            "participants": [],
            "date": NO_DATE,
            "time": "14:00",
            "end_time": "17:00",
            "locations": [],
        },
    },
    {
        "id": "time_range_T3",
        "text": "Call with team between 9am and 10:30am",
        "expected": {
            "task": True,
            "participants": ["team"],
            "date": NO_DATE,
            "time": "09:00",
            "end_time": "10:30",
            "locations": [],
        },
    },

    # ── Edge cases ────────────────────────────────────────────────────────────
    {
        "id": "edge_01_person_vs_city",
        "text": "Meet Paris for coffee at 10am",
        "expected": {
            "task": True,
            "participants": ["Paris"],
            "date": NO_DATE,
            "time": "10:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "edge_02_multi_participant",
        "text": "Study session with Alice and Bob at the library on Monday at 4pm",
        "expected": {
            "task": True,
            "participants": ["Alice", "Bob"],
            "date": ANY_DATE,
            "time": "16:00",
            "end_time": None,
            "locations": ["library"],
        },
    },
    {
        "id": "edge_03_no_time",
        "text": "Submit assignment on Wednesday",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": None,
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "edge_04_implicit_today",
        "text": "Team standup at 9:30am",
        "expected": {
            "task": True,
            "participants": [],
            "date": NO_DATE,
            "time": "09:30",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "edge_05_12pm",
        "text": "Lunch meeting at 12pm",
        "expected": {
            "task": True,
            "participants": [],
            "date": NO_DATE,
            "time": "12:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "edge_06_midnight",
        "text": "Submit report by midnight on Friday",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": "00:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "edge_07_location_with_at",
        "text": "Presentation at the lecture hall at 2pm on Tuesday",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": "14:00",
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "edge_08_no_entities",
        "text": "Buy milk",
        "expected": {
            "task": True,
            "participants": [],
            "date": NO_DATE,
            "time": None,
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "edge_09_next_week",
        "text": "Review pull requests next week",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": None,
            "end_time": None,
            "locations": [],
        },
    },
    {
        "id": "edge_10_am_pm_boundary",
        "text": "Morning run at 6:00am on Saturday",
        "expected": {
            "task": True,
            "participants": [],
            "date": ANY_DATE,
            "time": "06:00",
            "end_time": None,
            "locations": [],
        },
    },
]
