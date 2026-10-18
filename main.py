"""Temporary testing ground: run `python main.py` to check the PawPal+ logic in the terminal."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main():
    owner = Owner(name="Jordan", available_minutes=60)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high", time="08:00"))
    mochi.add_task(Task("Fetch in the yard", 20, "low", time="17:00"))
    luna.add_task(Task("Feeding", 10, "high", time="07:30"))
    luna.add_task(Task("Brushing", 15, "medium", time="19:00", frequency="weekly"))

    meds = Task("Flea meds", 5, "high", time="09:00", frequency="once")
    luna.add_task(meds)
    meds.mark_complete()

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("Today's Schedule")
    print("=" * 40)
    for task in sorted(plan, key=lambda t: t.time):
        print(f"{task.time}  {task.description:<15} {task.pet_name:<6} "
              f"{task.duration_minutes:>3} min  [{task.priority}]")

    print("\nWhy this plan")
    print("-" * 40)
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
