import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
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

    if st.button("Add task"):
        owner.pets[pet_index].add_task(Task(task_title, category, int(duration), priority))

tasks = owner.get_all_tasks()
if tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": task.pet_name,
                "title": task.title,
                "category": task.category,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
            }
            for task in tasks
        ]
    )
else:
    st.info("No tasks yet. Add a pet, then add a task.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
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
    st.markdown("**Why this plan:**")
    st.text(scheduler.explain_plan())
