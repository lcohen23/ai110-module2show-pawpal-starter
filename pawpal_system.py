from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str = "daily"
    preferred_time: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def reset_for_next_occurrence(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, task: Task, changes: dict) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_pending_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.plan: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def collect_tasks(self) -> list[Task]:
        pass

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def generate_plan(self) -> list[Task]:
        pass

    def detect_conflicts(self) -> list[str]:
        pass

    def explain_plan(self) -> str:
        pass
