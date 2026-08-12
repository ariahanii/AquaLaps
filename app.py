
"""
app.py

Streamlit UI for the swim training plan generator.
Collects a user profile, runs it through the RAG pipeline, and
displays the generated plan.

Run with: streamlit run app.py
"""

import sys
from pathlib import Path

# Make src/ importable from the project root
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from generate import generate_plan

import streamlit as st

from generate import generate_plan

st.set_page_config(page_title="AI Swim Training Planner", page_icon="🏊", layout="centered")

st.title("🏊 AquaLaps Personalised Swim Training Planner")
st.caption(
    "Generates a training plan grounded in swim science research papers. "
    "Educational — not medical or professional coaching advice."
)
GOAL_OPTIONS = [
    "improve 100m freestyle race time",
    "lose weight through swimming",
    "build general aerobic fitness",
    "improve stroke technique and efficiency",
    "Custom goal...",
]


goal_choice = st.selectbox("What's your main goal?", GOAL_OPTIONS)

custom_goal = ""
if goal_choice == "Custom goal...":
    custom_goal = st.text_input(
        "Describe your goal",
        placeholder="e.g. improve 200m breaststroke endurance for a masters competition",
    )

with st.form("profile_form"):
    st.subheader("Your profile")



    current_level = st.selectbox(
        "Current level",
        ["beginner", "intermediate", "advanced"],
    )

    days_per_week = st.slider("Days available per week", min_value=1, max_value=7, value=4)

    session_length_minutes = st.slider(
        "Session length (minutes)", min_value=20, max_value=120, value=60, step=10
    )

    notes = st.text_area(
        "Anything else worth knowing? (optional)",
        placeholder="e.g. shoulder injury history, comfortable with all four strokes, etc.",
    )

    submitted = st.form_submit_button("Generate my plan")

# ---- Generation + display ----
if submitted:
    goal = custom_goal.strip() if goal_choice == "Custom goal..." else goal_choice

    if not goal:
        st.error("Please enter a custom goal before generating a plan.")
        st.stop()

    user_profile = {
        "goal": goal,
        "current_level": current_level,
        "days_per_week": days_per_week,
        "session_length_minutes": session_length_minutes,
        "notes": notes or "none provided",
    }

    with st.spinner("Retrieving relevant research and generating your plan..."):
        try:
            plan = generate_plan(user_profile)
        except Exception as e:
            st.error(f"Something went wrong generating the plan: {e}")
            st.stop()

    st.success("Plan generated")

    st.subheader(plan.get("goal", goal))
    st.write(plan.get("overview", ""))

    for week in plan.get("weeks", []):
        with st.expander(f"Week {week.get('week_number')} — {week.get('focus', '')}", expanded=True):
            for session in week.get("sessions", []):
                st.markdown(f"**{session.get('day')} — {session.get('focus')}**")
                st.markdown(f"- Warm-up: {session.get('warm_up')}")
                st.markdown(f"- Main set: {session.get('main_set')}")
                st.markdown(f"- Cool-down: {session.get('cool_down')}")
                st.markdown(f"- Total distance: {session.get('total_distance_m')}m")
                st.divider()

    sources = plan.get("sources_used", [])
    if sources:
        st.caption("Sources referenced: " + ", ".join(sources))

    with st.expander("Raw JSON output"):
        st.json(plan)