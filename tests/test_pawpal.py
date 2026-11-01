from datetime import date

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

# Tests use fixed dates so results don't depend on the day they run.
TODAY = date(2026, 11, 2)
TOMORROW = date(2026, 11, 3)


def make_task(title="Task", duration=10, priority="high", **fields):
    fields.setdefault("due_date", TODAY)
    return Task(title, "walk", duration, priority, **fields)


def make_household(available_minutes=600, day_start="08:00", plan_date=TODAY):
    owner = Owner("Jordan", available_minutes)
    pet = Pet("Biscuit", "dog", 4)
    owner.add_pet(pet)
    return owner, pet, Scheduler(owner, day_start=day_start, plan_date=plan_date)


def plan_times(scheduler):
    return [(entry.start_time, entry.task.title) for entry in scheduler.plan]


def titles(tasks):
    return [task.title for task in tasks]


# Basics


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", "walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Biscuit", "dog", 4)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", "feeding", 10, "high"))

    assert len(pet.tasks) == 1


# Sorting


def test_sort_by_time_returns_chronological_order():
    _, _, scheduler = make_household()
    tasks = [
        make_task("Dinner", preferred_time="18:00"),
        make_task("Walk", preferred_time="07:30"),
        make_task("Lunch", preferred_time="12:00"),
    ]

    assert titles(scheduler.sort_by_time(tasks)) == ["Walk", "Lunch", "Dinner"]


def test_sort_by_time_puts_untimed_tasks_last():
    _, _, scheduler = make_household()
    tasks = [make_task("Untimed"), make_task("Timed", preferred_time="23:00")]

    assert titles(scheduler.sort_by_time(tasks)) == ["Timed", "Untimed"]


def test_sort_by_time_compares_times_as_numbers():
    _, _, scheduler = make_household()
    tasks = [make_task("Ten", preferred_time="10:00"), make_task("Seven", preferred_time="7:30")]

    assert titles(scheduler.sort_by_time(tasks)) == ["Seven", "Ten"]


def test_sort_tasks_orders_by_priority_then_duration():
    _, _, scheduler = make_household()
    tasks = [
        make_task("Low", 5, "low"),
        make_task("High long", 30, "high"),
        make_task("Medium", 10, "medium"),
        make_task("High short", 10, "high"),
    ]

    assert titles(scheduler.sort_tasks(tasks)) == ["High short", "High long", "Medium", "Low"]


# Plan building


def test_plan_is_returned_in_time_order():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Evening", preferred_time="18:00"))
    pet.add_task(make_task("Morning", preferred_time="09:00"))
    pet.add_task(make_task("Flexible"))

    scheduler.generate_plan()

    assert plan_times(scheduler) == [
        ("08:00", "Flexible"),
        ("09:00", "Morning"),
        ("18:00", "Evening"),
    ]


def test_flexible_task_too_long_for_gap_moves_later():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Fixed", 30, preferred_time="08:10"))
    pet.add_task(make_task("Flexible", 15))

    scheduler.generate_plan()

    assert plan_times(scheduler) == [("08:10", "Fixed"), ("08:40", "Flexible")]


def test_pet_with_no_tasks_gets_empty_plan():
    _, _, scheduler = make_household()

    assert scheduler.generate_plan() == []
    assert scheduler.explain_plan() == "No tasks to schedule."


def test_owner_with_no_pets_gets_empty_plan():
    scheduler = Scheduler(Owner("Jordan", 60), plan_date=TODAY)

    assert scheduler.generate_plan() == []
    assert scheduler.explain_plan() == "No tasks to schedule."


def test_task_exactly_filling_available_time_is_scheduled():
    _, pet, scheduler = make_household(available_minutes=30)
    pet.add_task(make_task("Walk", 30))

    scheduler.generate_plan()

    assert plan_times(scheduler) == [("08:00", "Walk")]
    assert scheduler.skipped_tasks == []


def test_no_available_time_skips_every_task():
    _, pet, scheduler = make_household(available_minutes=0)
    pet.add_task(make_task("Walk"))

    assert scheduler.generate_plan() == []
    assert titles(scheduler.skipped_tasks) == ["Walk"]


def test_generating_plan_twice_does_not_duplicate_tasks():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Walk"))

    scheduler.generate_plan()
    scheduler.generate_plan()

    assert len(scheduler.plan) == 1


# Recurring tasks


def test_completing_daily_task_creates_task_for_next_day():
    _, pet, _ = make_household()
    task = make_task("Meds", frequency="daily")
    pet.add_task(task)

    next_task = pet.complete_task(task, TODAY)

    assert task.completed is True
    assert next_task in pet.tasks
    assert next_task is not task
    assert next_task.due_date == TOMORROW
    assert next_task.completed is False
    assert next_task.pet_name == "Biscuit"


def test_completing_weekly_task_creates_task_seven_days_later():
    _, pet, _ = make_household()
    task = make_task("Bath", frequency="weekly")
    pet.add_task(task)

    next_task = pet.complete_task(task, TODAY)

    assert next_task.due_date == date(2026, 11, 9)


def test_overdue_daily_task_recurs_from_completion_date():
    _, pet, _ = make_household()
    task = make_task("Meds", frequency="daily", due_date=date(2026, 10, 28))
    pet.add_task(task)

    next_task = pet.complete_task(task, TODAY)

    assert next_task.due_date == TOMORROW


def test_weekly_task_completed_early_keeps_its_schedule():
    _, pet, _ = make_household()
    task = make_task("Bath", frequency="weekly", due_date=date(2026, 11, 6))
    pet.add_task(task)

    next_task = pet.complete_task(task, TODAY)

    assert next_task.due_date == date(2026, 11, 13)


def test_recurrence_rolls_over_to_next_year():
    _, pet, _ = make_household()
    new_years_eve = date(2026, 12, 31)
    task = make_task("Meds", frequency="daily", due_date=new_years_eve)
    pet.add_task(task)

    next_task = pet.complete_task(task, new_years_eve)

    assert next_task.due_date == date(2027, 1, 1)


def test_completing_task_twice_does_not_add_second_copy():
    _, pet, _ = make_household()
    task = make_task("Meds", frequency="daily")
    pet.add_task(task)

    pet.complete_task(task, TODAY)
    second_result = pet.complete_task(task, TODAY)

    assert second_result is None
    assert len(pet.tasks) == 2


def test_one_off_task_does_not_recur():
    _, pet, _ = make_household()
    task = make_task("Vet visit", frequency="once")
    pet.add_task(task)

    assert pet.complete_task(task, TODAY) is None
    assert len(pet.tasks) == 1


def test_next_occurrence_appears_in_plan_on_its_due_date():
    owner, pet, _ = make_household()
    task = make_task("Meds", frequency="daily")
    pet.add_task(task)
    pet.complete_task(task, TODAY)

    scheduler = Scheduler(owner, plan_date=TOMORROW)
    scheduler.generate_plan()

    assert plan_times(scheduler) == [("08:00", "Meds")]


# Due dates


def test_task_due_tomorrow_is_not_planned_today():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Walk", due_date=TOMORROW))

    assert scheduler.generate_plan() == []


def test_overdue_task_is_planned_today():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Walk", due_date=date(2026, 10, 1)))

    scheduler.generate_plan()

    assert plan_times(scheduler) == [("08:00", "Walk")]


def test_daily_task_completed_today_does_not_reappear_today():
    _, pet, scheduler = make_household()
    task = make_task("Meds", frequency="daily")
    pet.add_task(task)
    pet.complete_task(task, TODAY)

    assert scheduler.generate_plan() == []


def test_plan_stays_the_same_until_regenerated():
    _, pet, scheduler = make_household()
    task = make_task("Meds", frequency="daily")
    pet.add_task(task)
    scheduler.generate_plan()

    pet.complete_task(task, TODAY)
    assert plan_times(scheduler) == [("08:00", "Meds")]

    scheduler.generate_plan()
    assert scheduler.plan == []


# Filtering


def make_filter_household():
    owner, biscuit, _ = make_household()
    mochi = Pet("Mochi", "cat", 7)
    owner.add_pet(mochi)
    done_walk = make_task("Done walk")
    biscuit.add_task(done_walk)
    biscuit.add_task(make_task("Open walk"))
    mochi.add_task(make_task("Open meds"))
    done_walk.mark_complete()
    return owner


def test_filter_tasks_by_pet():
    owner = make_filter_household()

    assert titles(owner.filter_tasks(pet_name="Mochi")) == ["Open meds"]


def test_filter_tasks_by_incomplete_status():
    owner = make_filter_household()

    assert titles(owner.filter_tasks(completed=False)) == ["Open walk", "Open meds"]


def test_filter_tasks_by_completed_status():
    owner = make_filter_household()

    assert titles(owner.filter_tasks(completed=True)) == ["Done walk"]


def test_filter_tasks_by_pet_and_status():
    owner = make_filter_household()

    assert titles(owner.filter_tasks(pet_name="Biscuit", completed=False)) == ["Open walk"]


def test_filter_tasks_with_no_filters_returns_everything():
    owner = make_filter_household()

    assert len(owner.filter_tasks()) == 3


def test_filter_tasks_with_unknown_pet_returns_nothing():
    owner = make_filter_household()

    assert owner.filter_tasks(pet_name="Nobody") == []


def test_incomplete_filter_includes_tasks_not_yet_due():
    owner, pet, _ = make_household()
    pet.add_task(make_task("Next week", due_date=date(2026, 11, 9)))

    assert titles(owner.filter_tasks(completed=False)) == ["Next week"]


# Conflict detection


def test_two_tasks_at_same_time_are_flagged():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Walk", preferred_time="09:00"))
    pet.add_task(make_task("Meds", preferred_time="09:00"))

    scheduler.generate_plan()

    assert len(scheduler.detect_conflicts()) == 1
    assert "Walk" in scheduler.detect_conflicts()[0]
    assert "Meds" in scheduler.detect_conflicts()[0]


def test_conflict_appears_in_plan_explanation():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Walk", preferred_time="09:00"))
    pet.add_task(make_task("Meds", preferred_time="09:00"))

    scheduler.generate_plan()

    assert "Conflict:" in scheduler.explain_plan()


def test_partially_overlapping_tasks_are_flagged():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Walk", 30, preferred_time="09:00"))
    pet.add_task(make_task("Meds", 5, preferred_time="09:15"))

    scheduler.generate_plan()

    assert len(scheduler.detect_conflicts()) == 1


def test_back_to_back_tasks_do_not_conflict():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Walk", 30, preferred_time="09:00"))
    pet.add_task(make_task("Meds", 5, preferred_time="09:30"))

    scheduler.generate_plan()

    assert scheduler.detect_conflicts() == []


def test_long_task_conflicts_with_each_task_inside_it():
    _, pet, scheduler = make_household()
    pet.add_task(make_task("Long", 60, preferred_time="08:00"))
    pet.add_task(make_task("First", 5, preferred_time="08:10"))
    pet.add_task(make_task("Second", 5, preferred_time="08:30"))

    scheduler.generate_plan()

    assert len(scheduler.detect_conflicts()) == 2


def test_conflict_between_different_pets_is_flagged():
    owner, biscuit, scheduler = make_household()
    mochi = Pet("Mochi", "cat", 7)
    owner.add_pet(mochi)
    biscuit.add_task(make_task("Walk", preferred_time="09:00"))
    mochi.add_task(make_task("Meds", preferred_time="09:00"))

    scheduler.generate_plan()

    assert len(scheduler.detect_conflicts()) == 1


# Validation and day limits


def test_unknown_frequency_is_rejected():
    with pytest.raises(ValueError):
        _, pet, _ = make_household()
        task = make_task("Meds", frequency="monthly")
        pet.add_task(task)
        pet.complete_task(task, TODAY)


def test_frequency_ignores_capitalization():
    _, pet, _ = make_household()
    task = make_task("Bath", frequency="Weekly")
    pet.add_task(task)

    next_task = pet.complete_task(task, TODAY)

    assert next_task is not None
    assert next_task.due_date == date(2026, 11, 9)


def test_completing_another_pets_task_is_rejected():
    _, biscuit, _ = make_household()
    mochi = Pet("Mochi", "cat", 7)
    task = make_task("Walk")
    biscuit.add_task(task)

    with pytest.raises(ValueError):
        mochi.complete_task(task, TODAY)


@pytest.mark.parametrize("bad_time", ["25:00", "morning"])
def test_invalid_preferred_time_is_rejected(bad_time):
    with pytest.raises(ValueError, match=bad_time):
        _, pet, scheduler = make_household()
        pet.add_task(make_task("Walk", preferred_time=bad_time))
        scheduler.generate_plan()


def test_invalid_priority_is_rejected():
    with pytest.raises(ValueError, match="urgent"):
        _, pet, scheduler = make_household()
        pet.add_task(make_task("Walk", priority="urgent"))
        scheduler.generate_plan()


def test_flexible_task_past_midnight_is_skipped():
    _, pet, scheduler = make_household(available_minutes=1440, day_start="23:00")
    pet.add_task(make_task("Long", 90))
    pet.add_task(make_task("First", 30))
    pet.add_task(make_task("Second", 30))

    scheduler.generate_plan()

    assert titles(scheduler.skipped_tasks) == ["Long"]


def test_skip_message_reports_minutes_left_when_skipped():
    _, pet, scheduler = make_household(available_minutes=30)
    pet.add_task(make_task("Big", 20, "high"))
    pet.add_task(make_task("Medium", 15, "medium"))
    pet.add_task(make_task("Tiny", 5, "low"))

    scheduler.generate_plan()

    assert "only 10 min left" in scheduler.explain_plan()


def test_invalid_edit_leaves_task_unchanged():
    _, pet, _ = make_household()
    task = make_task("Walk", 30)
    pet.add_task(task)

    with pytest.raises(ValueError):
        pet.edit_task(task, {"duration_minutes": 45, "priority": "urgent"})

    assert task.duration_minutes == 30
    assert task.priority == "high"


def test_flexible_task_ending_exactly_at_midnight_is_scheduled():
    _, pet, scheduler = make_household(day_start="23:30")
    pet.add_task(make_task("Late walk", 30))

    scheduler.generate_plan()

    assert plan_times(scheduler) == [("23:30", "Late walk")]


def test_task_past_midnight_explains_why_it_was_skipped():
    _, pet, scheduler = make_household(day_start="23:30")
    pet.add_task(make_task("Late walk", 31))

    scheduler.generate_plan()

    assert "no open time left today" in scheduler.explain_plan()
