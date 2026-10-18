"""PawPal+ logic layer: backend classes for planning pet care tasks."""

from dataclasses import dataclass, field
from typing import List, Tuple

# Numeric rank for each priority so sorting isn't alphabetical ("high" < "low" < "medium").
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    category: str = "general"
    completed: bool = False
    pet_name: str = ""  # set by Pet.add_task so the scheduler knows who the task is for

    def __post_init__(self):
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and tag it with this pet's name."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass


@dataclass
class Owner:
    """A pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        pass


class Scheduler:
    """Selects and orders tasks into a daily plan for an owner."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: List[Task] = []
        self.skipped: List[Tuple[Task, str]] = []  # (task, reason it was left out)

    def generate_plan(self) -> List[Task]:
        """Build the daily plan from the owner's incomplete tasks within their available time.

        Fills self.plan with chosen tasks and self.skipped with (task, reason) for the rest.
        """
        pass

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered from highest to lowest priority, using PRIORITY_RANK."""
        pass

    def fits_in_time(self, task: Task, remaining: int) -> bool:
        """Return True if the task fits in the remaining minutes."""
        pass

    def explain_plan(self) -> str:
        """Explain which tasks were chosen and why the skipped ones were left out.

        Call generate_plan() first.
        """
        pass
