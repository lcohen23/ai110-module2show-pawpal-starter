import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet care planning assistant. Add your pets and their care tasks, and it
builds a daily plan around your available time, task priorities, and preferred times.
"""
)

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Time available today (minutes)", min_value=0, max_value=1440, value=60
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, available_minutes=int(available_minutes))

owner = st.session_state.owner
owner.name = owner_name
owner.available_minutes = int(available_minutes)

st.markdown("### Pets")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Enter a pet name.")
    elif any(pet.name == pet_name for pet in owner.pets):
        st.error(f"{pet_name} has already been added.")
    else:
        owner.add_pet(Pet(pet_name, species, int(age)))

if owner.pets:
    st.write("Current pets:")
    st.table(
        [{"name": pet.name, "species": pet.species, "age": pet.age} for pet in owner.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    pet_index = st.selectbox(
        "Pet",
        range(len(owner.pets)),
        format_func=lambda index: owner.pets[index].name,
    )

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "enrichment", "grooming"]
        )

    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col1, col2 = st.columns(2)
    with col1:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
    with col2:
        preferred_time = st.text_input("Preferred time (HH:MM, optional)")

    if st.button("Add task"):
        try:
            task = Task(
                task_title,
                category,
                int(duration),
                priority,
                frequency=frequency,
                preferred_time=preferred_time.strip(),
            )
        except ValueError as error:
            st.error(str(error))
        else:
            owner.pets[pet_index].add_task(task)

scheduler = Scheduler(owner)

pending_tasks = scheduler.sort_by_time(owner.filter_tasks(completed=False))
if pending_tasks:
    task_index = st.selectbox(
        "Task to complete",
        range(len(pending_tasks)),
        format_func=lambda index: (
            f"{pending_tasks[index].title} ({pending_tasks[index].pet_name}, "
            f"due {pending_tasks[index].due_date})"
        ),
    )
    if st.button("Mark complete"):
        task = pending_tasks[task_index]
        pet = next(pet for pet in owner.pets if pet.name == task.pet_name)
        next_task = pet.complete_task(task)
        if next_task:
            st.success(f"{task.title} is done. Next one is due {next_task.due_date}.")
        else:
            st.success(f"{task.title} is done.")

if owner.get_all_tasks():
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox(
            "Show pet", ["All pets"] + [pet.name for pet in owner.pets]
        )
    with col2:
        status_filter = st.selectbox("Show status", ["All", "Pending", "Completed"])

    filtered_tasks = owner.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    if filtered_tasks:
        st.table(
            [
                {
                    "time": task.preferred_time or "flexible",
                    "title": task.title,
                    "pet": task.pet_name,
                    "category": task.category,
                    "minutes": task.duration_minutes,
                    "priority": task.priority,
                    "frequency": task.frequency,
                    "due": str(task.due_date),
                    "status": "done" if task.completed else "pending",
                }
                for task in scheduler.sort_by_time(filtered_tasks)
            ]
        )
    else:
        st.info("No tasks match these filters.")
else:
    st.info("No tasks yet. Add a pet, then add a task.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    st.session_state.show_schedule = True

# Rebuilt on every rerun, so the schedule stays visible and reflects the latest tasks.
if st.session_state.get("show_schedule"):
    plan = scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()

    if plan:
        used_minutes = sum(entry.task.duration_minutes for entry in plan)
        st.success(
            f"Planned {len(plan)} task(s) using {used_minutes} of "
            f"{owner.available_minutes} available minutes."
        )
    for conflict in conflicts:
        st.warning(
            f"**Time conflict:** {conflict}. Change one of the preferred times, "
            "unless you can do both together."
        )
    if plan:
        st.table(
            [
                {
                    "time": entry.start_time,
                    "task": entry.task.title,
                    "pet": entry.task.pet_name,
                    "minutes": entry.task.duration_minutes,
                    "priority": entry.task.priority,
                }
                for entry in plan
            ]
        )
    if scheduler.skipped_tasks:
        st.warning(f"{len(scheduler.skipped_tasks)} task(s) didn't fit today:")
        st.table(
            [
                {
                    "task": task.title,
                    "pet": task.pet_name,
                    "minutes": task.duration_minutes,
                    "priority": task.priority,
                    "reason": scheduler.skip_reasons[task],
                }
                for task in scheduler.skipped_tasks
            ]
        )
    if plan or scheduler.skipped_tasks:
        with st.expander("Why this plan"):
            st.text(scheduler.explain_plan())
    else:
        st.info("No tasks are due today.")
