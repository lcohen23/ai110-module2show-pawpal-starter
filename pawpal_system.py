from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}
RECURRENCE_DAYS = {"once": None, "daily": 1, "weekly": 7}
MINUTES_PER_DAY = 24 * 60


def to_minutes(clock_time: str) -> int:
    """Convert an "HH:MM" string to minutes after midnight."""
    try:
        hours, minutes = (int(part) for part in clock_time.split(":"))
    except ValueError:
        raise ValueError(f"Invalid time {clock_time!r}, expected HH:MM") from None
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError(f"Invalid time {clock_time!r}, expected HH:MM")
    return hours * 60 + minutes


def to_clock_time(minutes: int) -> str:
    """Convert minutes after midnight to an "HH:MM" string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# eq=False: tasks and pets compare by identity, so two identical walks stay distinct.
@dataclass(eq=False)
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str = "daily"
    preferred_time: str = ""
    completed: bool = False
    pet_name: str = ""
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Normalize the frequency and reject invalid field values."""
        self.frequency = self.frequency.lower()
        if self.frequency not in RECURRENCE_DAYS:
            raise ValueError(f"Unknown frequency {self.frequency!r}")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"Unknown priority {self.priority!r}")
        if self.preferred_time:
            to_minutes(self.preferred_time)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self, today: date) -> Task | None:
        """Return a copy of this task for its next due date, or None if it doesn't recur."""
        days = RECURRENCE_DAYS[self.frequency]
        if days is None:
            return None
        # Counting from the later date keeps late and early completions on schedule.
        next_due = max(self.due_date, today) + timedelta(days=days)
        return replace(self, completed=False, due_date=next_due)


@dataclass
class ScheduledTask:
    task: Task
    start_time: str

    @property
    def start_minutes(self) -> int:
        """Return the start time as minutes after midnight."""
        return to_minutes(self.start_time)

    @property
    def end_minutes(self) -> int:
        """Return the end time as minutes after midnight."""
        return self.start_minutes + self.task.duration_minutes


@dataclass(eq=False)
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and label it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, task: Task, changes: dict) -> None:
        """Update the given fields on a task, rejecting unknown field names."""
        for name, value in changes.items():
            if not hasattr(task, name):
                raise ValueError(f"Task has no field named {name!r}")
        # Building a copy runs validation before the real task changes.
        updated = replace(task, **changes)
        for name in changes:
            setattr(task, name, getattr(updated, name))

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def complete_task(self, task: Task, today: date | None = None) -> Task | None:
        """Complete a task and add its next occurrence, returning the new task if any."""
        if task not in self.tasks:
            raise ValueError(f"{task.title!r} does not belong to {self.name}")
        if task.completed:
            return None
        task.mark_complete()
        next_task = task.next_occurrence(today or date.today())
        if next_task:
            self.tasks.append(next_task)
        return next_task

    def get_pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Return tasks matching the given pet name and completion status, if provided."""
        return [
            task
            for task in self.get_all_tasks()
            if (pet_name is None or task.pet_name == pet_name)
            and (completed is None or task.completed == completed)
        ]


class Scheduler:
    def __init__(
        self, owner: Owner, day_start: str = "08:00", plan_date: date | None = None
    ) -> None:
        """Create a scheduler for an owner with an empty plan."""
        self.owner = owner
        self.day_start = day_start
        self.plan_date = plan_date or date.today()
        self.plan: list[ScheduledTask] = []
        self.skipped_tasks: list[Task] = []
        self.skip_reasons: dict[Task, str] = {}

    def collect_tasks(self) -> list[Task]:
        """Return incomplete tasks due on or before the plan date."""
        return [
            task
            for task in self.owner.get_all_tasks()
            if not task.completed and task.due_date <= self.plan_date
        ]

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by highest priority, then shortest duration."""
        return sorted(
            tasks,
            key=lambda task: (-PRIORITY_RANK[task.priority], task.duration_minutes),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by preferred time, with untimed tasks last."""
        return sorted(
            tasks,
            key=lambda task: (
                to_minutes(task.preferred_time) if task.preferred_time else float("inf")
            ),
        )

    def generate_plan(self) -> list[ScheduledTask]:
        """Build today's plan from the available time and return it in time order."""
        self.plan = []
        self.skipped_tasks = []
        self.skip_reasons = {}

        # Highest priority tasks claim the available minutes first.
        selected = []
        remaining = self.owner.available_minutes
        for task in self.sort_tasks(self.collect_tasks()):
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
            else:
                self._skip(task, f"only {remaining} min left")

        # Tasks with a preferred time are fixed, then the rest fill the gaps around them.
        for task in selected:
            if task.preferred_time:
                self.plan.append(ScheduledTask(task, task.preferred_time))
        for task in selected:
            if not task.preferred_time:
                start = self._find_open_start(task.duration_minutes)
                if start + task.duration_minutes <= MINUTES_PER_DAY:
                    self.plan.append(ScheduledTask(task, to_clock_time(start)))
                else:
                    self._skip(task, "no open time left today")

        self.plan.sort(key=lambda entry: entry.start_minutes)
        return self.plan

    def _skip(self, task: Task, reason: str) -> None:
        """Record that a task was left out of the plan and why."""
        self.skipped_tasks.append(task)
        self.skip_reasons[task] = reason

    def _find_open_start(self, duration_minutes: int) -> int:
        """Return the earliest start in minutes where a task fits without overlap."""
        start = to_minutes(self.day_start)
        for entry in sorted(self.plan, key=lambda entry: entry.start_minutes):
            if start + duration_minutes <= entry.start_minutes:
                break
            start = max(start, entry.end_minutes)
        return start

    def detect_conflicts(self) -> list[str]:
        """Return a description of each pair of overlapping tasks in the plan."""
        conflicts = []
        for index, first in enumerate(self.plan):
            for second in self.plan[index + 1:]:
                if second.start_minutes < first.end_minutes:
                    conflicts.append(
                        f"{first.task.title} ({first.task.pet_name}) at {first.start_time} "
                        f"overlaps {second.task.title} ({second.task.pet_name}) "
                        f"at {second.start_time}"
                    )
        return conflicts

    def explain_plan(self) -> str:
        """Return a readable explanation of scheduled, skipped, and conflicting tasks."""
        if not self.plan and not self.skipped_tasks:
            return "No tasks to schedule."

        lines = []
        for entry in self.plan:
            task = entry.task
            reason = f"{task.priority} priority"
            if task.preferred_time:
                reason += ", at its preferred time"
            lines.append(
                f"{entry.start_time} - {task.title} for {task.pet_name} "
                f"({task.duration_minutes} min): {reason}"
            )

        for task in self.skipped_tasks:
            lines.append(
                f"Skipped {task.title} for {task.pet_name} "
                f"({task.duration_minutes} min): {self.skip_reasons[task]}"
            )

        for conflict in self.detect_conflicts():
            lines.append(f"Conflict: {conflict}")

        return "\n".join(lines)
