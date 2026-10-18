"""Tests for the PawPal+ logic layer."""

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
