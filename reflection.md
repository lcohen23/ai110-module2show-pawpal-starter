# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Enter owner and pet information,** including the time available for pet care today.
2. **Add and edit care tasks,** each with at least a duration and a priority.
3. **Generate and view today's plan,** with an explanation of why it was chosen.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML had four classes: an owner has many pets, a pet has many tasks, and the scheduler works from the owner.

- **Owner** holds the owner's details and pets, and gathers tasks across all pets.
- **Pet** holds a pet's details and manages its tasks.
- **Task** represents one care activity and tracks its completion.
- **Scheduler** holds the logic: it sorts tasks, builds the plan, detects conflicts, and explains its choices.

I used dataclasses for the first three because they mainly store data. Keeping the logic in Scheduler means the rules can change without touching them.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. I asked my AI assistant to review the skeleton, and made three changes based on its feedback:

- **Added `ScheduledTask` and `Scheduler.day_start`,** because a plain list of tasks had nowhere to store start times.
- **Added `Task.pet_name`,** because the flat task list lost track of whose task it was.
- **Added `PRIORITY_RANK`,** because sorting priority strings is alphabetical, which puts "low" above "medium".

Later, I replaced `reset_for_next_occurrence()` with `next_occurrence()` and `Pet.complete_task()`, because a recurring task needs a new copy with its own due date.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

It considers available minutes, priority, preferred times, and due dates. `Owner.preferences` is stored but doesn't affect the plan yet.

Time comes first because it's the hard limit. Priority decides who gets those minutes, since missing meds is worse than missing grooming, and shorter tasks go first within a priority level so more fit.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler warns about conflicts instead of resolving them, so a plan can contain two tasks at once. This is reasonable because the owner chose those times and knows things the scheduler doesn't, like whether two tasks can be combined. Silently moving medication to a different time would be worse than showing a warning.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used my AI coding assistant in every phase, from brainstorming classes to implementation, UI wiring, and documentation. Its most effective features were multi-file edits, such as adding recurring tasks across `pawpal_system.py` and `main.py`, and reviewing existing code, which found real gaps in my skeleton.

The most helpful prompts were specific and pointed at a file or method. Asking "what's missing?" worked better than "is this good?".

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I asked how to simplify `detect_conflicts()`, the assistant offered a one-expression version using `itertools.combinations` and a faster version with an early exit. I kept my nested loops: the first was harder to read and no faster, and the second relied on the plan staying sorted for a speedup nobody would notice.

I also had it undo an `app.py` edit when the step had only asked me to investigate `st.session_state`.

I verified suggestions by running `main.py` and `python -m pytest` and reading the output, not just the code.

**c. AI strategy**

- How did using separate chat sessions for different phases help you stay organized?

Separate sessions kept each phase focused, so algorithm planning didn't get mixed up with core implementation. Restating the goal in each new session also clarified what I wanted.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

My 49 tests cover sorting, plan building, recurring tasks, due dates, filtering, conflict detection, validation, and tasks near midnight. They matter because a plan can look fine while quietly dropping a task or duplicating a recurring one, which is serious for something like medication.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Based on test results, I'm confident: all 49 tests pass. Next I would test the Streamlit UI itself and overlaps between a late-night task and the next day's plan.

**Known limitations:** The scheduler plans one day at a time, so a fixed-time task can run past midnight and an overlap across midnight isn't detected. I kept those tasks in the plan because skipping something like meds would be worse than letting it run late.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Keeping the logic separate from the UI. The same classes run in `main.py`, the tests, and the Streamlit app, so I could prove the scheduler worked before connecting it to a page.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add task editing and removal to the UI, save data across page refreshes, and make `Owner.preferences` affect the plan.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Being the "lead architect" means the AI can write code quickly, but the decisions stay with me. I have to set the scope, judge each suggestion against the design, and check the results myself. Having the UML written first gave me a plan to judge against.
