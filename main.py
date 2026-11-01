from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler) -> None:
    print(f"Today's Schedule for {scheduler.owner.name}")
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


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)

    biscuit = Pet("Biscuit", "dog", 4)
    mochi = Pet("Mochi", "cat", 7)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", "walk", 30, "high", preferred_time="07:30"))
    biscuit.add_task(Task("Breakfast", "feeding", 10, "high"))
    biscuit.add_task(Task("Brush coat", "grooming", 45, "low"))
    mochi.add_task(Task("Thyroid meds", "meds", 5, "high", preferred_time="08:00"))
    mochi.add_task(Task("Puzzle feeder", "enrichment", 20, "medium", preferred_time="18:00"))

    scheduler = Scheduler(owner, day_start="07:00")
    scheduler.generate_plan()
    print_schedule(scheduler)


if __name__ == "__main__":
    main()
