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

# --- Owner (kept in session_state so it survives reruns) ---
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_minutes = st.number_input(
        "Minutes available today", min_value=1, max_value=1440, value=60
    )

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
owner = st.session_state.owner
owner.name = owner_name
owner.available_minutes = int(available_minutes)

# --- Add a pet ---
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=40, value=3)

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Please enter a pet name.")
    elif any(p.name == pet_name for p in owner.pets):
        st.warning(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
        st.success(f"Added {pet_name}.")

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# --- Add a task ---
st.subheader("Add a Task")
if not owner.pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    col1, col2 = st.columns(2)
    with col1:
        task_pet = st.selectbox("For which pet?", pet_names)
        description = st.text_input("Task description", value="Morning walk")
        task_time = st.time_input("Preferred time (optional)", value=None)
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add task"):
        pet = owner.pets[pet_names.index(task_pet)]
        try:
            pet.add_task(
                Task(
                    description=description,
                    duration_minutes=int(duration),
                    priority=priority,
                    time=task_time.strftime("%H:%M") if task_time else "",
                    frequency=frequency,
                )
            )
            st.success(f"Added '{description}' for {pet.name}.")
        except ValueError as e:
            st.error(str(e))

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": t.pet_name,
                "task": t.description,
                "time": t.time or "any",
                "minutes": t.duration_minutes,
                "priority": t.priority,
                "frequency": t.frequency,
                "done": t.completed,
            }
            for t in all_tasks
        ]
    )

st.divider()

# --- Build schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    if plan:
        st.markdown("#### Today's Schedule")
        st.table(
            [
                {
                    "time": t.time or "any",
                    "task": t.description,
                    "pet": t.pet_name,
                    "minutes": t.duration_minutes,
                    "priority": t.priority,
                }
                for t in sorted(plan, key=lambda t: t.time or "99:99")
            ]
        )
    else:
        st.warning("Nothing could be scheduled. Add tasks or increase your available minutes.")
    st.markdown("#### Why this plan")
    st.text(scheduler.explain_plan())
