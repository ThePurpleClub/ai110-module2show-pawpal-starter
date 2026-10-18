"""Tests for the PawPal+ logic layer."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def owner():
    """An owner with two pets and a mix of tasks."""
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Morning walk", 30, "high", time="08:00"))
    mochi.add_task(Task("Fetch", 20, "low", time="17:00"))
    luna.add_task(Task("Feeding", 10, "high", time="07:30"))
    luna.add_task(Task("Brushing", 15, "medium", time="19:00"))
    return owner


# --- Task ---

def test_mark_complete_sets_completed():
    task = Task("Feeding", 10, "high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration_minutes": 0},
        {"priority": "urgent"},
        {"frequency": "monthly"},
    ],
)
def test_task_rejects_invalid_values(kwargs):
    args = {"description": "Walk", "duration_minutes": 10, "priority": "low", **kwargs}
    with pytest.raises(ValueError):
        Task(**args)


# --- Pet ---

def test_add_task_increases_task_count():
    pet = Pet(name="Mochi", species="dog")
    before = len(pet.tasks)
    pet.add_task(Task("Walk", 30, "high"))
    assert len(pet.tasks) == before + 1


def test_add_task_tags_task_with_pet_name():
    pet = Pet(name="Mochi", species="dog")
    task = Task("Walk", 30, "high")
    pet.add_task(task)
    assert task.pet_name == "Mochi"


def test_remove_task():
    pet = Pet(name="Mochi", species="dog")
    task = Task("Walk", 30, "high")
    pet.add_task(task)
    pet.remove_task(task)
    assert pet.tasks == []


# --- Owner ---

def test_get_all_tasks_combines_every_pet(owner):
    tasks = owner.get_all_tasks()
    assert len(tasks) == 4
    assert {t.pet_name for t in tasks} == {"Mochi", "Luna"}


# --- Scheduler ---

def test_sort_by_priority_is_not_alphabetical():
    tasks = [Task("A", 10, "low"), Task("B", 10, "medium"), Task("C", 10, "high")]
    ordered = Scheduler(Owner("J", 60)).sort_by_priority(tasks)
    assert [t.priority for t in ordered] == ["high", "medium", "low"]


def test_sort_by_priority_breaks_ties_with_shorter_task():
    tasks = [Task("Long", 30, "high"), Task("Short", 5, "high")]
    ordered = Scheduler(Owner("J", 60)).sort_by_priority(tasks)
    assert [t.description for t in ordered] == ["Short", "Long"]


def test_plan_stays_within_available_time(owner):
    plan = Scheduler(owner).generate_plan()
    assert sum(t.duration_minutes for t in plan) <= owner.available_minutes


def test_plan_uses_tasks_from_all_pets(owner):
    plan = Scheduler(owner).generate_plan()
    assert {t.pet_name for t in plan} == {"Mochi", "Luna"}


def test_task_that_does_not_fit_is_skipped_with_reason(owner):
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    skipped = {t.description: reason for t, reason in scheduler.skipped}
    assert "Fetch" in skipped
    assert "min left" in skipped["Fetch"]


def test_completed_tasks_are_not_scheduled(owner):
    owner.pets[1].tasks[0].mark_complete()  # Luna's feeding
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    assert "Feeding" not in [t.description for t in plan]
    assert ("Feeding", "already completed") in [(t.description, r) for t, r in scheduler.skipped]


def test_no_tasks_gives_empty_plan():
    scheduler = Scheduler(Owner("J", 60))
    assert scheduler.generate_plan() == []
    assert "No plan yet" in scheduler.explain_plan()


def test_explain_plan_mentions_scheduled_and_skipped(owner):
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    text = scheduler.explain_plan()
    assert "Morning walk for Mochi" in text
    assert "Skipped:" in text


# --- Scheduler.sort_by_time ---

def test_sort_by_time_orders_tasks_chronologically(owner):
    scheduler = Scheduler(owner)
    result = scheduler.sort_by_time(owner.get_all_tasks())
    assert [t.time for t in result] == ["07:30", "08:00", "17:00", "19:00"]


def test_sort_by_time_puts_untimed_tasks_last():
    scheduler = Scheduler(Owner(name="Sam", available_minutes=60))
    tasks = [Task("Play", 10), Task("Dinner", 10, time="18:00"), Task("Breakfast", 10, time="07:00")]
    result = scheduler.sort_by_time(tasks)
    assert [t.description for t in result] == ["Breakfast", "Dinner", "Play"]


def test_sort_by_time_does_not_modify_input():
    scheduler = Scheduler(Owner(name="Sam", available_minutes=60))
    tasks = [Task("Dinner", 10, time="18:00"), Task("Breakfast", 10, time="07:00")]
    scheduler.sort_by_time(tasks)
    assert [t.description for t in tasks] == ["Dinner", "Breakfast"]


# --- Scheduler.filter_tasks ---

def test_filter_tasks_with_no_filters_returns_all(owner):
    assert len(Scheduler(owner).filter_tasks()) == 4


def test_filter_tasks_by_pet_name(owner):
    result = Scheduler(owner).filter_tasks(pet_name="Luna")
    assert [t.description for t in result] == ["Feeding", "Brushing"]


def test_filter_tasks_by_completion_status(owner):
    owner.pets[0].tasks[0].mark_complete()  # Mochi's morning walk
    scheduler = Scheduler(owner)
    assert [t.description for t in scheduler.filter_tasks(completed=True)] == ["Morning walk"]
    assert len(scheduler.filter_tasks(completed=False)) == 3


def test_filter_tasks_by_pet_and_status(owner):
    owner.pets[0].tasks[0].mark_complete()
    result = Scheduler(owner).filter_tasks(completed=False, pet_name="Mochi")
    assert [t.description for t in result] == ["Fetch"]


def test_filter_tasks_unknown_pet_returns_empty(owner):
    assert Scheduler(owner).filter_tasks(pet_name="Rex") == []


# --- Recurring tasks ---

def test_mark_complete_returns_next_daily_occurrence():
    task = Task("Feeding", 10, "high", time="07:30", frequency="daily", due_date=date(2026, 10, 18))
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is not task
    assert next_task.completed is False
    assert next_task.due_date == date(2026, 10, 19)
    assert (next_task.description, next_task.time, next_task.priority) == ("Feeding", "07:30", "high")


def test_weekly_task_recurs_seven_days_later():
    task = Task("Brushing", 15, frequency="weekly", due_date=date(2026, 10, 18))
    assert task.mark_complete().due_date == date(2026, 10, 25)


def test_once_task_does_not_recur():
    task = Task("Vet visit", 60, frequency="once")
    assert task.mark_complete() is None


def test_pet_complete_task_adds_next_occurrence():
    pet = Pet(name="Mochi", species="dog")
    walk = Task("Walk", 30, frequency="daily")
    pet.add_task(walk)
    next_walk = pet.complete_task(walk)
    assert pet.tasks == [walk, next_walk]
    assert next_walk.pet_name == "Mochi"


def test_scheduler_complete_task_finds_the_right_pet(owner):
    luna = owner.pets[1]
    feeding = luna.tasks[0]
    next_feeding = Scheduler(owner).complete_task(feeding)
    assert next_feeding in luna.tasks
    assert len(owner.pets[0].tasks) == 2  # Mochi's tasks are untouched


def test_scheduler_complete_task_rejects_unknown_task(owner):
    with pytest.raises(ValueError):
        Scheduler(owner).complete_task(Task("Stray task", 5))


def test_next_occurrence_is_not_planned_until_due(owner):
    scheduler = Scheduler(owner)
    feeding = owner.pets[1].tasks[0]
    next_feeding = scheduler.complete_task(feeding)

    today_plan = scheduler.generate_plan(today=feeding.due_date)
    assert next_feeding not in today_plan
    assert any(t is next_feeding and r.startswith("not due until") for t, r in scheduler.skipped)

    tomorrow_plan = scheduler.generate_plan(today=next_feeding.due_date)
    assert any(t is next_feeding for t in tomorrow_plan)


# --- Scheduler.detect_conflicts ---

def test_no_conflicts_in_fixture(owner):
    assert Scheduler(owner).detect_conflicts() == []


def test_same_time_different_pets_is_a_conflict(owner):
    owner.pets[0].add_task(Task("Vet call", 10, time="07:30"))  # Mochi, same time as Luna's feeding
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "Feeding" in warnings[0] and "Vet call" in warnings[0]
    assert "Luna and Mochi" in warnings[0] or "Mochi and Luna" in warnings[0]


def test_same_pet_overlap_is_a_conflict(owner):
    owner.pets[0].add_task(Task("Bath", 15, time="08:15"))  # during Mochi's 08:00-08:30 walk
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "both for Mochi" in warnings[0]


def test_back_to_back_tasks_do_not_conflict(owner):
    owner.pets[0].add_task(Task("Breakfast", 10, time="08:30"))  # starts right as the walk ends
    assert Scheduler(owner).detect_conflicts() == []


def test_untimed_completed_and_other_day_tasks_are_ignored(owner):
    mochi = owner.pets[0]
    mochi.add_task(Task("Play", 30))  # no time
    done = Task("Old walk", 30, time="08:00")
    mochi.add_task(done)
    done.mark_complete()
    mochi.add_task(Task("Tomorrow walk", 30, time="08:00", due_date=date.today() + timedelta(days=1)))
    assert Scheduler(owner).detect_conflicts() == []


def test_long_task_conflicts_with_several_later_tasks():
    owner = Owner(name="Sam", available_minutes=120)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task("Hike", 90, time="09:00"))
    pet.add_task(Task("Snack", 5, time="09:30"))
    pet.add_task(Task("Water", 5, time="10:00"))
    assert len(Scheduler(owner).detect_conflicts()) == 2


def test_generate_plan_reports_conflicts_in_explanation(owner):
    owner.pets[0].add_task(Task("Vet call", 10, "high", time="07:30"))
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    assert len(scheduler.conflicts) == 1
    assert "Warnings:" in scheduler.explain_plan()


def test_invalid_time_gives_warning_instead_of_crashing(owner):
    owner.pets[0].add_task(Task("Mystery task", 10, time="8am"))
    owner.pets[1].add_task(Task("Late snack", 5, time="25:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 2
    assert all("not a valid HH:MM time" in w for w in warnings)


def test_invalid_time_does_not_hide_real_conflicts(owner):
    owner.pets[0].add_task(Task("Mystery task", 10, time="soon"))
    owner.pets[0].add_task(Task("Vet call", 10, time="07:30"))
    warnings = Scheduler(owner).detect_conflicts()
    assert any("not a valid" in w for w in warnings)
    assert any("Feeding" in w and "Vet call" in w for w in warnings)
