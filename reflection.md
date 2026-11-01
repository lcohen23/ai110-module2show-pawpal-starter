# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Enter owner and pet information.** The user records basic details about themselves and their pet, such as the pet's name and species and how much time they have available for pet care today.
2. **Add and edit care tasks.** The user manages the tasks their pet needs, such as walks, feeding, meds, enrichment, and grooming, giving each one at least a duration and a priority.
3. **Generate and view today's plan.** The user asks for a daily schedule and sees which tasks fit within their available time and priorities, along with an explanation of why the plan was chosen.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML had four classes, split so that three hold data and one makes decisions. An owner has many pets, a pet has many tasks, and the scheduler works from the owner.

- **Owner** holds the owner's name, available minutes, preferences, and pets. It adds and removes pets and gathers the tasks across all of them, so it is the scheduler's single entry point to the data.
- **Pet** holds a pet's name, species, age, and tasks. It adds, edits, and removes tasks and returns the ones still pending.
- **Task** represents one care activity, with its title, category, duration, priority, frequency, preferred time, and completion status. It can mark itself complete and reset for its next occurrence.
- **Scheduler** holds the scheduling logic. It collects and sorts tasks, fits them into the available time to build a plan, tracks what was skipped, detects conflicts, and explains its choices.

I used dataclasses for Owner, Pet, and Task because they mainly store data, and a regular class for Scheduler because it is mostly behavior. Keeping the logic in Scheduler means the scheduling rules can change without touching the data classes.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. I asked my AI assistant to review the skeleton for missing relationships and logic bottlenecks, and made three changes based on its feedback:

- **Added a `ScheduledTask` class and `Scheduler.day_start`.** The plan was a plain list of tasks, which left nowhere to store when each task happens. `ScheduledTask` pairs a task with its start time, and `day_start` gives the scheduler a time to count from. Keeping start times out of `Task` means regenerating a plan doesn't change the tasks themselves.
- **Added `Task.pet_name`.** `Owner.get_all_tasks()` returns one flat list, so a task lost its link to its pet. With more than one pet, the plan and its explanation couldn't say whose walk it was.
- **Added a `PRIORITY_RANK` lookup.** Priorities are strings, so sorting them directly would be alphabetical and put "high" before "medium" but "low" before "medium". The lookup gives them a numeric order.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
