# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

First section of the terminal output from running `python main.py`. The rest of the demo shows sorting, filtering, recurring tasks, and conflict warnings:

```
Today's Schedule for Jordan
========================================================
Time   Task              Pet        Min  Priority
--------------------------------------------------------
07:00  Breakfast         Biscuit     10  high
07:30  Morning walk      Biscuit     30  high
08:00  Thyroid meds      Mochi        5  high
18:00  Puzzle feeder     Mochi       20  medium

Why this plan:
  07:00 - Breakfast for Biscuit (10 min): high priority
  07:30 - Morning walk for Biscuit (30 min): high priority, at its preferred time
  08:00 - Thyroid meds for Mochi (5 min): high priority, at its preferred time
  18:00 - Puzzle feeder for Mochi (20 min): medium priority, at its preferred time
  Skipped Brush coat for Biscuit (45 min): only 25 min left
```

## 🧪 Testing PawPal+

Run the full test suite:

```bash
python -m pytest
```

### What the tests cover

The 49 test cases in `tests/test_pawpal.py` cover each main behavior, including happy paths and edge cases:

- **Sorting:** chronological order, untimed tasks last, and priority then duration
- **Plan building:** filling gaps around fixed tasks, exact time fits, no tasks, no pets, and no available time
- **Recurring tasks:** daily and weekly repeats, late and early completion, year rollover, and double completion
- **Due dates:** overdue tasks, tasks not yet due, and plans that only change when regenerated
- **Filtering:** by pet, by status, by both, and by an unknown pet
- **Conflict detection:** duplicate times, partial overlaps, back-to-back tasks, and conflicts between pets
- **Validation and day limits:** invalid frequencies, priorities, and times, rejected edits, and tasks that run past midnight

### Test output

```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\liamb\OneDrive\Documents\GitHub\ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 49 items

tests\test_pawpal.py .................................................   [100%]

============================= 49 passed in 0.07s ==============================
```

### Confidence Level

⭐⭐⭐⭐⭐ (5/5)

Based on test results, all 49 tests pass, covering the scheduling logic's main behaviors and edge cases.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time()` orders tasks by preferred time, with untimed tasks last. `sort_tasks()` orders by highest priority, then shortest duration, which decides who gets the available minutes first. |
| Filtering | `Owner.filter_tasks()`, `Scheduler.collect_tasks()`, `Scheduler.generate_plan()` | `filter_tasks()` filters by pet name, completion status, or both. `collect_tasks()` keeps incomplete tasks due on or before the plan date. `generate_plan()` skips tasks that don't fit in the available time, and flexible tasks that would run past midnight. |
| Conflict handling | `Scheduler.detect_conflicts()` | Compares start and end times of planned tasks, for the same pet or different pets, and returns a warning message for each overlapping pair. It never moves a task or raises an error. Tasks without a preferred time fill open gaps, so only tasks with fixed preferred times can conflict. |
| Recurring tasks | `Pet.complete_task()`, `Task.next_occurrence()` | Completing a daily or weekly task adds a new copy due 1 or 7 days later, using `timedelta`. The date counts from today or the task's due date, whichever is later. A `once` task doesn't repeat, and any other frequency raises a `ValueError`. |
| Input validation | `Task.__post_init__()`, `to_minutes()`, `Pet.edit_task()`, `Pet.complete_task()` | Invalid frequencies, priorities, and times raise a `ValueError`. Edits are checked before they change a task, and a pet can't complete another pet's task. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
