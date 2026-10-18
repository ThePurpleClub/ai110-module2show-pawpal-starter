"""PawPal+ logic layer: backend classes for planning pet care tasks."""

from dataclasses import dataclass, field
from typing import List, Tuple

# Numeric rank for each priority so sorting isn't alphabetical ("high" < "low" < "medium").
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    description: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", or "high"
    time: str = ""  # preferred start time as "HH:MM", or "" for any time
    frequency: str = "daily"  # "once", "daily", or "weekly"
    completed: bool = False
    pet_name: str = ""  # set by Pet.add_task so the scheduler knows who the task is for

    def __post_init__(self):
        """Reject invalid duration, priority, or frequency values."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and tag it with this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """A pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Selects and orders tasks into a daily plan for an owner."""

    def __init__(self, owner: Owner):
        """Create a scheduler for an owner with an empty plan."""
        self.owner = owner
        self.plan: List[Task] = []
        self.skipped: List[Tuple[Task, str]] = []  # (task, reason it was left out)

    def generate_plan(self) -> List[Task]:
        """Pick incomplete tasks by priority that fit in the owner's time; record the rest as skipped."""
        self.plan = []
        self.skipped = []
        remaining = self.owner.available_minutes

        pending = []
        for task in self.owner.get_all_tasks():
            if task.completed:
                self.skipped.append((task, "already completed"))
            else:
                pending.append(task)

        for task in self.sort_by_priority(pending):
            if self.fits_in_time(task, remaining):
                self.plan.append(task)
                remaining -= task.duration_minutes
            else:
                self.skipped.append(
                    (task, f"needs {task.duration_minutes} min but only {remaining} min left")
                )
        return self.plan

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks from highest to lowest priority, shorter tasks first on ties."""
        return sorted(tasks, key=lambda t: (-PRIORITY_RANK[t.priority], t.duration_minutes))

    def fits_in_time(self, task: Task, remaining: int) -> bool:
        """Return True if the task fits in the remaining minutes."""
        return task.duration_minutes <= remaining

    def explain_plan(self) -> str:
        """Explain which tasks were chosen and why others were skipped (call generate_plan first)."""
        if not self.plan and not self.skipped:
            return "No plan yet. Add tasks and call generate_plan() first."

        used = sum(t.duration_minutes for t in self.plan)
        lines = [
            f"Plan for {self.owner.name}: {used} of {self.owner.available_minutes} min used.",
            "Tasks are chosen by priority (high first), shorter tasks first on ties.",
        ]
        for i, t in enumerate(self.plan, 1):
            when = f" at {t.time}" if t.time else ""
            lines.append(
                f"  {i}. {t.description} for {t.pet_name}{when}"
                f" ({t.duration_minutes} min, {t.priority} priority, {t.frequency})"
            )
        if self.skipped:
            lines.append("Skipped:")
            for t, reason in self.skipped:
                lines.append(f"  - {t.description} for {t.pet_name}: {reason}")
        return "\n".join(lines)
