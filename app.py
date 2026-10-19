from datetime import date

import pandas as pd
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

scheduler = Scheduler(owner)

PRIORITY_LABELS = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def due_label(day):
    """Show today and tomorrow by name, other days as e.g. "Sun, Oct 25"."""
    offset = (day - date.today()).days
    if offset == 0:
        return "Today"
    if offset == 1:
        return "Tomorrow"
    if offset < 0:
        return f"Overdue ({day:%b %d})"
    return f"{day:%a, %b %d}"


def task_table(tasks, show_status=True):
    """Show tasks as a numbered table with readable labels."""
    rows = []
    for t in tasks:
        row = {
            "Due": due_label(t.due_date),
            "Time": t.time or "Any time",
            "Pet": t.pet_name,
            "Task": t.description,
            "Duration": f"{t.duration_minutes} min",
            "Priority": PRIORITY_LABELS[t.priority],
            "Repeats": t.frequency.capitalize(),
        }
        if show_status:
            row["Status"] = "✅ Done" if t.completed else "⏳ To do"
        rows.append(row)
    st.table(pd.DataFrame(rows, index=range(1, len(rows) + 1)))


# --- Current tasks: filtered and sorted by the Scheduler ---
if owner.get_all_tasks():
    st.subheader("Current Tasks")
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["All", "To do", "Done"])

    tasks = scheduler.filter_tasks(
        completed={"All": None, "To do": False, "Done": True}[status_filter],
        pet_name=None if pet_filter == "All pets" else pet_filter,
    )
    # Conflicts across every pet, so the owner sees clashes before building a plan.
    conflicts = scheduler.detect_conflicts()

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks shown", len(tasks))
    col2.metric("Still to do", sum(not t.completed for t in tasks))
    col3.metric("Time conflicts", len(conflicts))

    if tasks:
        task_table(scheduler.sort_by_time(tasks))
        st.caption("Sorted by due date, then time. Tasks with no set time are listed last each day.")
    else:
        st.info("No tasks match these filters.", icon="🔍")

    if conflicts:
        for warning in conflicts:
            st.warning(warning, icon="⚠️")
    else:
        st.success("No time conflicts across your pets.", icon="✅")

    # --- Complete a task (recurring tasks schedule their next occurrence) ---
    st.subheader("Complete a Task")
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"), icon="🎉")
    todo = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if todo:
        choice = st.selectbox(
            "Task",
            range(len(todo)),
            format_func=lambda i: (
                f"{todo[i].pet_name}: {todo[i].description} "
                f"({due_label(todo[i].due_date)}{', ' + todo[i].time if todo[i].time else ''})"
            ),
        )
        if st.button("Mark complete"):
            task = todo[choice]
            next_task = scheduler.complete_task(task)
            # Saved for after the rerun, which refreshes the task table above.
            if next_task:
                st.session_state.flash = (
                    f"Completed '{task.description}' for {task.pet_name}. Next {task.frequency} "
                    f"occurrence is due {due_label(next_task.due_date).lower()}."
                )
            else:
                st.session_state.flash = (
                    f"Completed '{task.description}' for {task.pet_name}. It doesn't repeat."
                )
            st.rerun()
    else:
        st.success("Everything is done!", icon="🎉")

st.divider()

# --- Build schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_plan()
    used = sum(t.duration_minutes for t in plan)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks scheduled", len(plan))
    col2.metric("Minutes used", f"{used} / {owner.available_minutes}")
    col3.metric("Minutes free", owner.available_minutes - used)
    st.progress(used / owner.available_minutes, text="Time budget used")

    if plan:
        st.markdown("#### Today's Schedule")
        task_table(scheduler.sort_by_time(plan), show_status=False)
        st.caption("Chosen by priority (high first, shorter first on ties), shown in time order.")
    else:
        st.warning(
            "Nothing could be scheduled. Add tasks or increase your available minutes.", icon="📭"
        )

    if scheduler.conflicts:
        st.markdown("#### Conflicts in this plan")
        for warning in scheduler.conflicts:
            st.warning(warning, icon="⚠️")
    elif plan:
        st.success("No time conflicts in today's plan.", icon="✅")

    # "needs N min" reasons mean the task ran out of time; the rest weren't needed today.
    no_time = [(t, r) for t, r in scheduler.skipped if r.startswith("needs")]
    not_today = [(t, r) for t, r in scheduler.skipped if not r.startswith("needs")]
    if no_time:
        st.markdown("#### Didn't fit today")
        st.warning(
            f"{len(no_time)} task(s) didn't fit in your {owner.available_minutes} minutes. "
            "Free up time or raise their priority.",
            icon="⏰",
        )
        st.table(
            pd.DataFrame(
                [
                    {"Pet": t.pet_name, "Task": t.description,
                     "Priority": PRIORITY_LABELS[t.priority], "Reason": r}
                    for t, r in no_time
                ],
                index=range(1, len(no_time) + 1),
            )
        )
    if not_today:
        with st.expander(f"Not needed today ({len(not_today)})"):
            st.table(
                pd.DataFrame(
                    [{"Pet": t.pet_name, "Task": t.description, "Reason": r} for t, r in not_today],
                    index=range(1, len(not_today) + 1),
                )
            )

    with st.expander("Why this plan"):
        st.text(scheduler.explain_plan())
