"""PawPal+ logic layer: backend classes for planning pet care tasks."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    category: str = "general"
    completed: bool = False

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
        """Add a care task for this pet."""
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

    def generate_plan(self) -> List[Task]:
        """Build the daily plan from the owner's tasks within their available time."""
        pass

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered from highest to lowest priority."""
        pass

    def fits_in_time(self, task: Task, remaining: int) -> bool:
        """Return True if the task fits in the remaining minutes."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        pass
