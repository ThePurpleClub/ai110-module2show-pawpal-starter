"""PawPal+ logic layer: backend classes for planning pet care tasks."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import List, Optional, Tuple

# Numeric rank for each priority so sorting isn't alphabetical ("high" < "low" < "medium").
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
FREQUENCIES = ("once", "daily", "weekly")
# How far ahead the next occurrence of a recurring task is due ("once" tasks don't recur).
RECURRENCE_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


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
    due_date: date = field(default_factory=date.today)  # the day this occurrence is due

    def __post_init__(self):
        """Reject invalid duration, priority, or frequency values."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}")

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as done and return its next occurrence, or None if it doesn't recur.

        The returned task is not added to any pet; use Pet.complete_task for that.
        """
        self.completed = True
        return self.next_occurrence()

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh, incomplete copy due one interval later, or None for "once" tasks."""
        interval = RECURRENCE_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        return replace(self, completed=False, due_date=self.due_date + interval)


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

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if it recurs, add its next occurrence to this pet."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


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


def to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


class Scheduler:
    """Selects and orders tasks into a daily plan for an owner."""

    def __init__(self, owner: Owner):
        """Create a scheduler for an owner with an empty plan."""
        self.owner = owner
        self.plan: List[Task] = []
        self.skipped: List[Tuple[Task, str]] = []  # (task, reason it was left out)
        self.conflicts: List[str] = []  # overlap warnings for the current plan

    def generate_plan(self, today: Optional[date] = None) -> List[Task]:
        """Pick incomplete tasks due by today, by priority, that fit in the owner's time.

        Everything left out is recorded in self.skipped with a reason. Pass `today` to plan
        for a different day (defaults to date.today()).
        """
        today = today or date.today()
        self.plan = []
        self.skipped = []
        remaining = self.owner.available_minutes

        pending = []
        for task in self.owner.get_all_tasks():
            if task.completed:
                self.skipped.append((task, "already completed"))
            elif task.due_date > today:
                self.skipped.append((task, f"not due until {task.due_date.isoformat()}"))
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
        self.conflicts = self.detect_conflicts(self.plan)
        return self.plan

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks from highest to lowest priority, shorter tasks first on ties."""
        return sorted(tasks, key=lambda t: (-PRIORITY_RANK[t.priority], t.duration_minutes))

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks in clock order by their "HH:MM" time; tasks with no time go last."""
        # Zero-padded "HH:MM" strings sort correctly as plain strings, so no parsing is needed.
        # The key (t.time == "", t.time) puts False (has a time) before True (no time).
        return sorted(tasks, key=lambda t: (t.time == "", t.time))

    def filter_tasks(
        self, completed: Optional[bool] = None, pet_name: Optional[str] = None
    ) -> List[Task]:
        """Return the owner's tasks matching the given completion status and/or pet name.

        Leave a filter as None to ignore it; with no filters, every task is returned.
        """
        return [
            t
            for t in self.owner.get_all_tasks()
            if (completed is None or t.completed == completed)
            and (pet_name is None or t.pet_name == pet_name)
        ]

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return a warning for each pair of tasks whose time slots overlap on the same day.

        A task occupies [time, time + duration). Tasks with no time and completed tasks are
        ignored. Checks the given tasks, or all of the owner's tasks if none are given.
        Warnings are returned rather than raised so the app can still show the plan; a task
        with an unreadable time gets its own warning and is left out of the check.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        warnings = []
        timed = []
        for t in tasks:
            if not t.time or t.completed:
                continue
            # A malformed time ("8am", "25:00") becomes a warning instead of crashing the check.
            try:
                start = to_minutes(t.time)
            except ValueError:
                start = -1
            if not 0 <= start < 24 * 60:
                warnings.append(
                    f"Couldn't check '{t.description}' for {t.pet_name} for conflicts: "
                    f"time {t.time!r} is not a valid HH:MM time"
                )
                continue
            timed.append(t)
        timed.sort(key=lambda t: (t.due_date, to_minutes(t.time)))

        for i, first in enumerate(timed):
            first_end = to_minutes(first.time) + first.duration_minutes
            for second in timed[i + 1:]:
                # Sorted by start, so once a task starts after `first` ends, no later one overlaps.
                if second.due_date != first.due_date or to_minutes(second.time) >= first_end:
                    break
                who = (
                    f"both for {first.pet_name}"
                    if first.pet_name == second.pet_name
                    else f"{first.pet_name} and {second.pet_name}"
                )
                warnings.append(
                    f"Conflict on {first.due_date}: '{first.description}' at {first.time} "
                    f"({first.duration_minutes} min) overlaps '{second.description}' "
                    f"at {second.time} ({who})"
                )
        return warnings

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark one of the owner's tasks complete and schedule its next occurrence on its pet."""
        for pet in self.owner.pets:
            if any(t is task for t in pet.tasks):
                return pet.complete_task(task)
        raise ValueError(f"{task.description!r} does not belong to any of {self.owner.name}'s pets")

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
        if self.conflicts:
            lines.append("Warnings:")
            lines.extend(f"  ! {warning}" for warning in self.conflicts)
        if self.skipped:
            lines.append("Skipped:")
            for t, reason in self.skipped:
                lines.append(f"  - {t.description} for {t.pet_name}: {reason}")
        return "\n".join(lines)
