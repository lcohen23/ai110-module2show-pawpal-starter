from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler, heading: str = "Today's Schedule") -> None:
    print(f"{heading} for {scheduler.owner.name}")
    print("=" * 56)
    print(f"{'Time':<7}{'Task':<18}{'Pet':<10}{'Min':>4}  Priority")
    print("-" * 56)
    for entry in scheduler.plan:
        task = entry.task
        print(
            f"{entry.start_time:<7}{task.title:<18}{task.pet_name:<10}"
            f"{task.duration_minutes:>4}  {task.priority}"
        )
    print()
    print("Why this plan:")
    for line in scheduler.explain_plan().splitlines():
        print(f"  {line}")


def print_tasks(heading: str, tasks: list[Task]) -> None:
    print()
    print(heading)
    print("-" * 56)
    for task in tasks:
        time = task.preferred_time or "--:--"
        status = "done" if task.completed else "pending"
        print(f"{time:<7}{task.title:<18}{task.pet_name:<10}{status:<9}{task.due_date}")


def print_conflicts(scheduler: Scheduler) -> None:
    print()
    print("Conflict check")
    print("-" * 56)
    conflicts = scheduler.detect_conflicts()
    for conflict in conflicts:
        print(f"WARNING: {conflict}")
    if not conflicts:
        print("No conflicts found.")


def demo_conflicts() -> None:
    owner = Owner("Jordan", available_minutes=120)
    biscuit = Pet("Biscuit", "dog", 4)
    mochi = Pet("Mochi", "cat", 7)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Same pet at the same time.
    biscuit.add_task(Task("Morning walk", "walk", 30, "high", preferred_time="09:00"))
    biscuit.add_task(Task("Joint meds", "meds", 5, "high", preferred_time="09:00"))
    # Different pets at the same time.
    biscuit.add_task(Task("Lunch", "feeding", 10, "medium", preferred_time="12:00"))
    mochi.add_task(Task("Lunch", "feeding", 10, "medium", preferred_time="12:00"))
    # Starts right as lunch ends, so it should not be flagged.
    mochi.add_task(Task("Play time", "enrichment", 15, "low", preferred_time="12:10"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    print_conflicts(scheduler)


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)

    biscuit = Pet("Biscuit", "dog", 4)
    mochi = Pet("Mochi", "cat", 7)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Added out of time order so sort_by_time has something to do.
    morning_walk = Task("Morning walk", "walk", 30, "high", preferred_time="07:30")
    brush_coat = Task("Brush coat", "grooming", 45, "low", frequency="weekly")
    biscuit.add_task(brush_coat)
    biscuit.add_task(Task("Breakfast", "feeding", 10, "high"))
    biscuit.add_task(morning_walk)
    mochi.add_task(Task("Puzzle feeder", "enrichment", 20, "medium", preferred_time="18:00"))
    mochi.add_task(Task("Thyroid meds", "meds", 5, "high", preferred_time="08:00"))

    scheduler = Scheduler(owner, day_start="07:00")
    scheduler.generate_plan()
    print_schedule(scheduler)

    print_tasks("All tasks, as added", owner.get_all_tasks())
    print_tasks("Sorted by time", scheduler.sort_by_time(owner.get_all_tasks()))

    biscuit.complete_task(morning_walk)
    biscuit.complete_task(brush_coat)
    print_tasks("Mochi's tasks", owner.filter_tasks(pet_name="Mochi"))
    print_tasks("Completed tasks", owner.filter_tasks(completed=True))
    print_tasks("Biscuit's pending tasks", owner.filter_tasks(pet_name="Biscuit", completed=False))

    tomorrow = date.today() + timedelta(days=1)
    tomorrow_scheduler = Scheduler(owner, day_start="07:00", plan_date=tomorrow)
    tomorrow_scheduler.generate_plan()
    print()
    print_schedule(tomorrow_scheduler, heading="Tomorrow's Schedule")
    print_conflicts(tomorrow_scheduler)

    demo_conflicts()


if __name__ == "__main__":
    main()
