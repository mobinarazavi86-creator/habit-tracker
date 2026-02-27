import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"habits": [], "records": {}}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

st.set_page_config(page_title="My Habit Tracker", page_icon="🎯", layout="wide")

data = load_data()

st.sidebar.header("Control Center")

selected_date = st.sidebar.date_input("Select Date", datetime.today())
date_str = selected_date.strftime("%Y-%m-%d")

st.sidebar.subheader("Add New Habit")
new_habit = st.sidebar.text_input("Habit Name")
if st.sidebar.button("➕ Add", use_container_width=True):
    if new_habit and new_habit not in data["habits"]:
        data["habits"].append(new_habit)
        save_data(data)
        st.rerun()

st.sidebar.subheader("Manage Habits")
if data["habits"]:
    habit_to_delete = st.sidebar.selectbox("Select habit to delete", data["habits"])
    if st.sidebar.button("🗑️ Delete", use_container_width=True):
        data["habits"].remove(habit_to_delete)
        for d in data["records"]:
            if habit_to_delete in data["records"][d]:
                del data["records"][d][habit_to_delete]
        save_data(data)
        st.rerun()

st.title("🎯 My Habit Tracker")
st.markdown(f"**Date:** {date_str}")

if date_str not in data["records"]:
    data["records"][date_str] = {h: False for h in data["habits"]}
else:
    for h in data["habits"]:
        if h not in data["records"][date_str]:
            data["records"][date_str][h] = False

total_habits = len(data["habits"])
completed_habits = sum(1 for h, v in data["records"][date_str].items() if v and h in data["habits"])
success_rate = int((completed_habits / total_habits * 100)) if total_habits > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Habits", total_habits)
col2.metric("Completed", completed_habits)
col3.metric("Success Rate", f"{success_rate}%")

if total_habits > 0 and success_rate == 100:
    st.balloons()

st.divider()

st.subheader("Tasks")
for habit in data["habits"]:
    is_done = data["records"][date_str].get(habit, False)
    checked = st.checkbox(habit, value=is_done, key=f"chk_{habit}_{date_str}")
    if checked != is_done:
        data["records"][date_str][habit] = checked
        save_data(data)
        st.rerun()

st.divider()
st.subheader("Progress & Stats")

last_7_days = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
chart_data = []
for d in last_7_days:
    completed = sum(1 for h, v in data["records"].get(d, {}).items() if v and h in data["habits"])
    chart_data.append({"Date": d, "Completed": completed})

df = pd.DataFrame(chart_data)
fig = px.bar(df, x="Date", y="Completed", title="Last 7 Days Activity", text_auto=True, color_discrete_sequence=['#4CAF50'])
st.plotly_chart(fig, use_container_width=True)

current_month = datetime.today().strftime("%Y-%m")
month_total = 0
month_completed = 0
for d, records in data["records"].items():
    if d.startswith(current_month):
        for h, v in records.items():
            if h in data["habits"]:
                month_total += 1
                if v:
                    month_completed += 1

monthly_rate = int((month_completed / month_total * 100)) if month_total > 0 else 0
st.write(f"**Monthly Progress ({current_month}):** {monthly_rate}%")
st.progress(monthly_rate / 100.0)

st.subheader("Streaks")
for habit in data["habits"]:
    streak = 0
    check_date = datetime.today()
    while True:
        d_str = check_date.strftime("%Y-%m-%d")
        if data["records"].get(d_str, {}).get(habit, False):
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    if streak > 0:
        st.success(f"🔥 **{habit}:** {streak} days in a row!")
