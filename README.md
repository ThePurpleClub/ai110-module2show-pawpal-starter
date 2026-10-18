# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧩 Implementation Summary

PawPal+ keeps all backend logic in `pawpal_system.py`, in four classes (UML in `diagrams/uml.mmd`):

| Class | Role |
|-------|------|
| `Task` | One care activity: description, duration, priority (low/medium/high), preferred time, frequency (once/daily/weekly), and completion status. Rejects invalid values on creation. |
| `Pet` | A pet's details plus its list of tasks. `add_task()` tags each task with the pet's name. |
| `Owner` | The user, their available minutes for the day, and their pets. `get_all_tasks()` returns every pet's tasks in one list. |
| `Scheduler` | The "brain." Builds the daily plan from the owner's tasks and explains it. |

**How they work together:** an `Owner` has one or more `Pet`s, and each `Pet` has `Task`s. The `Scheduler` is given the `Owner` and reads tasks only through `Owner.get_all_tasks()`, so a single plan covers every pet. `generate_plan()` drops completed tasks, sorts the rest by priority (shorter tasks first on ties), and adds each task while it fits in the remaining time. Anything left out is recorded with a reason, and `explain_plan()` turns the chosen and skipped tasks into a plain-language summary.

`main.py` runs a two-pet demo in the terminal, and `tests/test_pawpal.py` covers the key behaviors (run with `pytest`).

## 🖥️ Sample Output

Output from running `python main.py` (owner Jordan, 60 minutes available, two pets with five tasks):

```
Today's Schedule
========================================
07:30  Feeding         Luna    10 min  [high]
08:00  Morning walk    Mochi   30 min  [high]
19:00  Brushing        Luna    15 min  [medium]

Why this plan
----------------------------------------
Plan for Jordan: 55 of 60 min used.
Tasks are chosen by priority (high first), shorter tasks first on ties.
  1. Feeding for Luna at 07:30 (10 min, high priority, daily)
  2. Morning walk for Mochi at 08:00 (30 min, high priority, daily)
  3. Brushing for Luna at 19:00 (15 min, medium priority, weekly)
Skipped:
  - Flea meds for Luna: already completed
  - Fetch in the yard for Mochi: needs 20 min but only 5 min left
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
