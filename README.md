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
| `Task` | One care activity: description, duration, priority (low/medium/high), preferred time (`"HH:MM"`), frequency (once/daily/weekly), due date, and completion status. Rejects invalid values on creation. Completing a daily or weekly task returns its next occurrence. |
| `Pet` | A pet's details plus its list of tasks. `add_task()` tags each task with the pet's name, and `complete_task()` marks a task done and adds its next occurrence. |
| `Owner` | The user, their available minutes for the day, and their pets. `get_all_tasks()` returns every pet's tasks in one list. |
| `Scheduler` | The "brain." Builds the daily plan, sorts and filters tasks, detects time conflicts, and explains the plan. |

**How they work together:** an `Owner` has one or more `Pet`s, and each `Pet` has `Task`s. The `Scheduler` is given the `Owner` and reads tasks only through `Owner.get_all_tasks()`, so a single plan covers every pet. `generate_plan()` drops completed tasks and tasks not due yet, sorts the rest by priority (shorter tasks first on ties), and adds each task while it fits in the remaining time. Anything left out is recorded with a reason, overlapping times are recorded as warnings, and `explain_plan()` turns it all into a plain-language summary. See [Smarter Scheduling](#-smarter-scheduling) for the sorting, filtering, conflict, and recurring-task features.

`main.py` runs a two-pet demo of every feature in the terminal, and `tests/test_pawpal.py` covers the key behaviors (run with `pytest`).

## 🖥️ Sample Output

Excerpts from running `python main.py` (owner Jordan, 60 minutes available, two pets; tasks are added out of time order on purpose). The full run also shows filtering and the plan explanation with warnings.

```
Sorted by time (untimed last)
--------------------------------------------------
  2026-10-18  07:30  Feeding            Luna    10 min  [high] (todo)
  2026-10-18  08:00  Morning walk       Mochi   30 min  [high] (todo)
  2026-10-18  09:00  Flea meds          Luna     5 min  [high] (done)
  2026-10-18  17:00  Fetch in the yard  Mochi   20 min  [low] (todo)
  2026-10-18  18:30  Evening walk       Mochi   20 min  [medium] (todo)
  2026-10-18  19:00  Brushing           Luna    15 min  [medium] (todo)
  2026-10-18  --:--  Playtime           Luna    10 min  [low] (todo)

Today's plan (chosen by priority, shown by time)
--------------------------------------------------
  2026-10-18  07:30  Feeding            Luna    10 min  [high] (todo)
  2026-10-18  08:00  Morning walk       Mochi   30 min  [high] (todo)
  2026-10-18  19:00  Brushing           Luna    15 min  [medium] (todo)

Why this plan
--------------------------------------------------
Plan for Jordan: 55 of 60 min used.
Tasks are chosen by priority (high first), shorter tasks first on ties.
  1. Feeding for Luna at 07:30 (10 min, high priority, daily)
  2. Morning walk for Mochi at 08:00 (30 min, high priority, daily)
  3. Brushing for Luna at 19:00 (15 min, medium priority, weekly)
Skipped:
  - Flea meds for Luna: already completed
  - Evening walk for Mochi: needs 20 min but only 5 min left
  - Playtime for Luna: needs 10 min but only 5 min left
  - Fetch in the yard for Mochi: needs 20 min but only 5 min left

Recurring tasks
--------------------------------------------------
  Completed 'Feeding' (daily)  -> next due 2026-10-19
  Completed 'Brushing' (weekly) -> next due 2026-10-25
  Completing a 'once' task returns: None

Conflict check (after adding same-time tasks)
--------------------------------------------------
  ! Couldn't check 'Window watching' for Luna for conflicts: time '3pm' is not a valid HH:MM time
  ! Conflict on 2026-10-18: 'Lunch' at 12:00 (10 min) overlaps 'Lunch' at 12:00 (Mochi and Luna)
  ! Conflict on 2026-10-18: 'Grooming' at 15:00 (20 min) overlaps 'Training' at 15:00 (both for Mochi)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# List each test by name:
python -m pytest -v
```

The 40 tests in `tests/test_pawpal.py` cover task validation, priority ordering, time budgets, skipped-task reasons, sorting by time, filtering by pet and status, recurring tasks and due dates, and conflict detection (including same-time tasks, back-to-back tasks, and malformed times).

Sample test output:

```
============================= test session starts ==============================
collected 40 items

tests/test_pawpal.py ........................................            [100%]

============================== 40 passed in 0.02s ==============================
```

## 📐 Smarter Scheduling

Beyond the basic priority plan, the `Scheduler` (in `pawpal_system.py`) adds four features. Each one is shown in `python main.py` and covered by tests in `tests/test_pawpal.py`.

| Feature | Method(s) | What it does |
|---------|-----------|--------------|
| Sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Orders tasks by clock time (untimed last) or by priority |
| Filtering | `Scheduler.filter_tasks()` | Returns tasks for one pet, by completion status, or both |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns when two tasks' time slots overlap |
| Recurring tasks | `Task.mark_complete()`, `Task.next_occurrence()`, `Pet.complete_task()`, `Scheduler.complete_task()` | Creates the next daily/weekly occurrence when a task is completed |

### Sorting: `Scheduler.sort_by_time()`

Returns a new list of tasks in clock order using the sort key `(t.time == "", t.time)`. Tasks with no preferred time go last, because `False` sorts before `True`. Zero-padded `"HH:MM"` strings sort correctly as plain text, so no time parsing is needed. The input list is not changed.

`Scheduler.sort_by_priority()` is used by `generate_plan()` to decide *which* tasks fit: high before medium before low (using the numeric `PRIORITY_RANK`, not alphabetical order), with shorter tasks first on ties. A common pattern is to choose by priority and then display by time:

```python
plan = scheduler.generate_plan()
for task in scheduler.sort_by_time(plan):
    ...
```

### Filtering: `Scheduler.filter_tasks(completed=None, pet_name=None)`

Returns the owner's tasks that match the given filters. Leaving a filter as `None` ignores it:

```python
scheduler.filter_tasks()                                # every task
scheduler.filter_tasks(pet_name="Luna")                 # only Luna's tasks
scheduler.filter_tasks(completed=False)                 # what's still to do
scheduler.filter_tasks(completed=False, pet_name="Mochi")  # Mochi's unfinished tasks
```

Filters and sorting combine, for example `scheduler.sort_by_time(scheduler.filter_tasks(completed=False))` lists today's remaining tasks in clock order. `generate_plan()` also filters on its own: it skips completed tasks and tasks whose `due_date` is after today, recording a reason for each.

### Conflict detection: `Scheduler.detect_conflicts(tasks=None)`

A lightweight check that **returns warning messages instead of raising errors**, so a clash never crashes the app.

- Each timed task occupies `[time, time + duration)`. Two tasks on the same day conflict if those windows overlap, which includes starting at exactly the same time. Back-to-back tasks (a 30-minute 08:00 walk and an 08:30 breakfast) do not conflict.
- It works for the same pet (`"both for Mochi"`) and for different pets (`"Mochi and Luna"`), since one owner can't do two things at once.
- Completed tasks and tasks with no time are ignored.
- A malformed time like `"3pm"` gets its own warning and is left out of the check, instead of crashing it.
- Tasks are sorted by start time first, so each task is only compared with the tasks that start before it ends.

`generate_plan()` runs this check on the chosen plan and stores the results in `scheduler.conflicts`, and `explain_plan()` prints them under **Warnings:**

```
Warnings:
  ! Couldn't check 'Window watching' for Luna for conflicts: time '3pm' is not a valid HH:MM time
  ! Conflict on 2026-10-18: 'Lunch' at 12:00 (10 min) overlaps 'Lunch' at 12:00 (Mochi and Luna)
  ! Conflict on 2026-10-18: 'Training' at 15:00 (15 min) overlaps 'Grooming' at 15:00 (both for Mochi)
```

### Recurring tasks: `Task.mark_complete()` and `Pet.complete_task()`

Each task has a `due_date` (defaults to today) and a `frequency` of `"once"`, `"daily"`, or `"weekly"`.

- `Task.next_occurrence()` returns a fresh, incomplete copy due 1 day later (daily) or 7 days later (weekly), or `None` for `"once"` tasks. It uses `dataclasses.replace()`, so the description, time, priority, and pet carry over.
- `Task.mark_complete()` marks the task done and returns its next occurrence, without adding it anywhere.
- `Pet.complete_task(task)` marks the task done **and** adds the next occurrence to that pet.
- `Scheduler.complete_task(task)` finds which pet owns the task and calls `Pet.complete_task()`.

```python
next_feeding = scheduler.complete_task(feeding)   # daily, due 2026-10-18
next_feeding.due_date                             # 2026-10-19
```

Because `generate_plan()` skips tasks that aren't due yet, tomorrow's copy doesn't appear in today's plan. It shows up as `"not due until 2026-10-19"` in the skipped list. Pass `generate_plan(today=...)` to plan for a different day.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
