"""Temporary testing ground: run `python main.py` to check the PawPal+ logic in the terminal."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title, tasks):
    """Print a heading and one line per task."""
    print(f"\n{title}")
    print("-" * 50)
    if not tasks:
        print("  (none)")
    for task in tasks:
        when = task.time or "--:--"
        status = "done" if task.completed else "todo"
        print(f"  {task.due_date}  {when}  {task.description:<18} {task.pet_name:<6} "
              f"{task.duration_minutes:>3} min  [{task.priority}] ({status})")


def print_warnings(warnings):
    """Print each warning, or a note that there are none."""
    if not warnings:
        print("  No conflicts.")
    for warning in warnings:
        print(f"  ! {warning}")


def main():
    owner = Owner(name="Jordan", available_minutes=60)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks are added deliberately out of time order to exercise sort_by_time.
    mochi.add_task(Task("Fetch in the yard", 20, "low", time="17:00"))
    luna.add_task(Task("Brushing", 15, "medium", time="19:00", frequency="weekly"))
    mochi.add_task(Task("Morning walk", 30, "high", time="08:00"))
    luna.add_task(Task("Playtime", 10, "low"))  # no preferred time
    luna.add_task(Task("Feeding", 10, "high", time="07:30"))
    mochi.add_task(Task("Evening walk", 20, "medium", time="18:30"))

    meds = Task("Flea meds", 5, "high", time="09:00", frequency="once")
    luna.add_task(meds)
    meds.mark_complete()

    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()

    print_tasks("All tasks (in the order they were added)", all_tasks)
    print_tasks("Sorted by time (untimed last)", scheduler.sort_by_time(all_tasks))
    print_tasks("Filter: Mochi's tasks", scheduler.filter_tasks(pet_name="Mochi"))
    print_tasks("Filter: completed tasks", scheduler.filter_tasks(completed=True))
    print_tasks(
        "Filter + sort: Luna's unfinished tasks by time",
        scheduler.sort_by_time(scheduler.filter_tasks(completed=False, pet_name="Luna")),
    )

    plan = scheduler.generate_plan()
    print_tasks("Today's plan (chosen by priority, shown by time)", scheduler.sort_by_time(plan))

    print("\nWhy this plan")
    print("-" * 50)
    print(scheduler.explain_plan())

    # Completing a recurring task schedules its next occurrence automatically.
    feeding = next(t for t in luna.tasks if t.description == "Feeding")
    brushing = next(t for t in luna.tasks if t.description == "Brushing")
    next_feeding = scheduler.complete_task(feeding)
    next_brushing = scheduler.complete_task(brushing)

    print("\nRecurring tasks")
    print("-" * 50)
    print(f"  Completed '{feeding.description}' (daily)  -> next due {next_feeding.due_date}")
    print(f"  Completed '{brushing.description}' (weekly) -> next due {next_brushing.due_date}")
    print(f"  Completing a 'once' task returns: {meds.next_occurrence()}")
    print_tasks("Luna's tasks after completing", scheduler.sort_by_time(luna.tasks))

    # --- Conflict detection ---
    # Before adding clashing tasks, the schedule should be conflict-free.
    print("\nConflict check (before)")
    print("-" * 50)
    print_warnings(scheduler.detect_conflicts())

    # Two tasks at exactly the same time (12:00): one for Mochi, one for Luna.
    mochi.add_task(Task("Lunch", 10, "high", time="12:00"))
    luna.add_task(Task("Lunch", 10, "high", time="12:00"))
    # Two tasks for the same pet at the same time (15:00).
    mochi.add_task(Task("Grooming", 20, "medium", time="15:00"))
    mochi.add_task(Task("Training", 15, "medium", time="15:00"))
    # A malformed time should produce a warning, not a crash.
    luna.add_task(Task("Window watching", 5, "low", time="3pm"))

    print("\nConflict check (after adding same-time tasks)")
    print("-" * 50)
    print_warnings(scheduler.detect_conflicts())

    # The same warnings appear in the plan explanation for whatever gets scheduled.
    owner.available_minutes = 120
    scheduler.generate_plan()
    print("\nPlan explanation with warnings")
    print("-" * 50)
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
