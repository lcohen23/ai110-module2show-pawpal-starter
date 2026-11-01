# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks for their pets.

## Scenario

A busy pet owner needs help staying consistent with pet care. PawPal+ tracks care tasks across their pets, fits them into the time available, and produces a daily plan that explains its choices.

## Features

- **Priority-based planning:** High-priority tasks claim the available minutes first, and skipped tasks come with a reason.
- **Fixed and flexible times:** Tasks with a preferred time stay put, and flexible tasks fill the earliest gaps.
- **Sorting by time:** Tasks run chronologically, with flexible tasks last.
- **Filtering:** View tasks by pet, completion status, or both.
- **Conflict warnings:** Overlapping tasks trigger a warning, for the same pet or across pets.
- **Daily and weekly recurrence:** Completing a recurring task creates its next occurrence.
- **Due dates:** Plans include tasks due today or overdue.
- **Plan explanations:** Each planned task shows why it was chosen.
- **Input validation:** Invalid priorities, frequencies, and times are rejected.

### Current limitations

- Tasks can't be edited or removed in the app, only in the logic layer.
- Refreshing the page clears all data.
- Owner preferences are stored but don't affect the plan yet.
- The app always plans from 08:00 today.

## System design

The logic lives in `pawpal_system.py`, separate from the UI, so `app.py`, `main.py`, and the tests all use the same classes.

| Class | Responsibility |
|-------|----------------|
| `Owner` | Holds the owner's details and pets, and gathers and filters tasks across them. |
| `Pet` | Holds a pet's details and manages its tasks. |
| `Task` | One care activity, with its duration, priority, frequency, due date, and status. |
| `ScheduledTask` | Pairs a `Task` with its start time in a plan. |
| `Scheduler` | Sorts tasks across all pets, builds the plan, detects conflicts, and explains its choices. |

The full class diagram is in `diagrams/uml_final.mmd`.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the terminal demo

```bash
python main.py
```

## 🧪 Testing PawPal+

Run the full test suite:

```bash
python -m pytest
```

### What the tests cover

The 49 test cases in `tests/test_pawpal.py` cover:

- **Sorting:** time order, and priority then duration
- **Plan building:** gaps around fixed tasks, exact fits, and empty cases
- **Recurring tasks:** daily, weekly, late and early completion, and year rollover
- **Due dates:** overdue tasks and tasks not yet due
- **Filtering:** by pet, status, or both
- **Conflict detection:** same times, partial overlaps, back-to-back tasks, and across pets
- **Validation and day limits:** invalid input and tasks past midnight

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

Based on test results: all 49 tests pass.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | By preferred time with untimed tasks last, or by priority then duration. |
| Filtering | `Owner.filter_tasks()`, `Scheduler.collect_tasks()` | By pet and completion status, or by tasks due on the plan date. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns a warning for each overlapping pair, across pets, without moving tasks. |
| Recurring tasks | `Pet.complete_task()`, `Task.next_occurrence()` | Adds a new copy due 1 or 7 days later, using `timedelta`. |
| Input validation | `Task.__post_init__()`, `to_minutes()` | Invalid frequencies, priorities, and times raise a `ValueError`. |

## 📸 Demo Walkthrough

### Main UI features

- **Owner:** Enter your name and available minutes.
- **Pets:** Add pets with a name, species, and age.
- **Tasks:** Add tasks to a pet, including frequency and an optional preferred time.
- **Task list:** Mark tasks complete, and filter a list sorted by time.
- **Build Schedule:** See the plan, conflict warnings, skipped tasks, and the reasoning. It stays visible and updates as tasks change.

### Example workflow

1. Set the time available to 60 minutes, then add two pets: Mochi and Biscuit.
2. Add these tasks:

   | Pet | Task | Minutes | Priority | Frequency | Preferred time |
   |-----|------|---------|----------|-----------|----------------|
   | Mochi | Meds | 5 | high | once | 09:00 |
   | Mochi | Dinner | 10 | high | daily | 18:00 |
   | Biscuit | Walk | 20 | high | daily | 09:00 |
   | Biscuit | Breakfast | 5 | medium | daily | |
   | Biscuit | Bath | 40 | low | weekly | |

3. Set "Show pet" to Mochi to filter the time-sorted task list.
4. Click **Generate schedule**. The summary reads "Planned 4 task(s) using 40 of 60 available minutes."
5. Read the warning that Meds and Walk overlap at 09:00.
6. Check the schedule: Breakfast takes the 08:00 slot, and Bath is skipped with "only 20 min left".
7. Mark Walk complete. The app shows its next due date, which is tomorrow, and the schedule updates so Bath now fits.

### Key Scheduler behaviors shown

- **Priority:** High-priority tasks claim time first, so Bath is skipped.
- **Sorting:** The task list and plan run in time order.
- **Filtering:** The dropdowns narrow tasks by pet and status.
- **Conflict warnings:** Meds and Walk are flagged, and neither moves.
- **Recurrence:** Completing Walk adds the next one, due tomorrow.

### Sample CLI output

Output from running `python main.py`, which uses its own example data:

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

All tasks, as added
--------------------------------------------------------
--:--  Brush coat        Biscuit   pending  2026-11-01
--:--  Breakfast         Biscuit   pending  2026-11-01
07:30  Morning walk      Biscuit   pending  2026-11-01
18:00  Puzzle feeder     Mochi     pending  2026-11-01
08:00  Thyroid meds      Mochi     pending  2026-11-01

Sorted by time
--------------------------------------------------------
07:30  Morning walk      Biscuit   pending  2026-11-01
08:00  Thyroid meds      Mochi     pending  2026-11-01
18:00  Puzzle feeder     Mochi     pending  2026-11-01
--:--  Brush coat        Biscuit   pending  2026-11-01
--:--  Breakfast         Biscuit   pending  2026-11-01

Mochi's tasks
--------------------------------------------------------
18:00  Puzzle feeder     Mochi     pending  2026-11-01
08:00  Thyroid meds      Mochi     pending  2026-11-01

Completed tasks
--------------------------------------------------------
--:--  Brush coat        Biscuit   done     2026-11-01
07:30  Morning walk      Biscuit   done     2026-11-01

Biscuit's pending tasks
--------------------------------------------------------
--:--  Breakfast         Biscuit   pending  2026-11-01
07:30  Morning walk      Biscuit   pending  2026-11-02
--:--  Brush coat        Biscuit   pending  2026-11-08

Tomorrow's Schedule for Jordan
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

Conflict check
--------------------------------------------------------
No conflicts found.

Conflict check
--------------------------------------------------------
WARNING: Joint meds (Biscuit) at 09:00 overlaps Morning walk (Biscuit) at 09:00
WARNING: Lunch (Biscuit) at 12:00 overlaps Lunch (Mochi) at 12:00
```
