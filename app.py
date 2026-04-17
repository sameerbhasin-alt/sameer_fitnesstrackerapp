# save as app.py
# run using: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="100 Day Fat Loss Tracker", layout="wide")

# -------------------------------
# CONFIG
# -------------------------------
CSV_FILE = "fat_loss_tracker.csv"

START_WEIGHT = 88
TARGET_WEIGHT = 74
TOTAL_DAYS = 100
DAILY_CAL_TARGET = 1850
DAILY_PROTEIN_TARGET = 150
DAILY_CARB_TARGET = 110
DAILY_FAT_TARGET = 55

# -------------------------------
# FUNCTIONS
# -------------------------------
def create_file():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "Date","Weight","Calories","Protein","Carbs","Fat",
            "Water","Steps","Workout","Sleep","Notes"
        ])
        df.to_csv(CSV_FILE, index=False)

def load_data():
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def expected_weight(day_no):
    loss_per_day = (START_WEIGHT - TARGET_WEIGHT) / TOTAL_DAYS
    return round(START_WEIGHT - (loss_per_day * day_no),2)

# -------------------------------
# INIT
# -------------------------------
create_file()
df = load_data()

st.title("🏋️ 100 Day Fat Loss Dashboard")
st.subheader("88 kg ➜ 74 kg in 100 Days")

# -------------------------------
# SIDEBAR ENTRY FORM
# -------------------------------
st.sidebar.header("➕ Daily Entry")

entry_date = st.sidebar.date_input("Date", date.today())
weight = st.sidebar.number_input("Weight (kg)", 40.0, 200.0, 88.0)
calories = st.sidebar.number_input("Calories", 0, 5000, 1800)
protein = st.sidebar.number_input("Protein (g)", 0, 300, 140)
carbs = st.sidebar.number_input("Carbs (g)", 0, 400, 110)
fat = st.sidebar.number_input("Fat (g)", 0, 200, 55)
water = st.sidebar.number_input("Water (Liters)", 0.0, 10.0, 3.5)
steps = st.sidebar.number_input("Steps", 0, 50000, 8000)
workout = st.sidebar.selectbox("Workout Done?", ["Yes", "No"])
sleep = st.sidebar.number_input("Sleep (hrs)", 0.0, 12.0, 7.0)
notes = st.sidebar.text_input("Notes")

if st.sidebar.button("Save Entry"):
    new_row = pd.DataFrame([{
        "Date": entry_date,
        "Weight": weight,
        "Calories": calories,
        "Protein": protein,
        "Carbs": carbs,
        "Fat": fat,
        "Water": water,
        "Steps": steps,
        "Workout": workout,
        "Sleep": sleep,
        "Notes": notes
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.drop_duplicates(subset=["Date"], keep="last", inplace=True)
    df = df.sort_values("Date")
    save_data(df)
    st.success("Entry Saved!")

# Reload updated data
df = load_data()

if len(df) > 0:
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Day"] = range(1, len(df)+1)
    df["Expected Weight"] = df["Day"].apply(expected_weight)

# -------------------------------
# KPI SECTION
# -------------------------------
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

if len(df) > 0:
    latest = df.iloc[-1]
    days_done = len(df)
    progress = round((days_done / TOTAL_DAYS) * 100,1)
    weight_lost = round(START_WEIGHT - latest["Weight"],2)

    col1.metric("Current Weight", f"{latest['Weight']} kg")
    col2.metric("Weight Lost", f"{weight_lost} kg")
    col3.metric("Day Progress", f"{days_done}/{TOTAL_DAYS}")
    col4.metric("Plan Completion", f"{progress}%")

# -------------------------------
# CHARTS
# -------------------------------
if len(df) > 0:

    st.markdown("## 📉 Weight Tracking")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Weight"],
        mode="lines+markers",
        name="Actual Weight"
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Expected Weight"],
        mode="lines",
        name="Target Path"
    ))

    st.plotly_chart(fig, use_container_width=True)

    # Nutrition Charts
    st.markdown("## 🍽 Nutrition Performance")

    c1, c2 = st.columns(2)

    with c1:
        fig2 = px.bar(
            df, x="Date", y=["Protein","Carbs","Fat"],
            barmode="group",
            title="Macros Intake"
        )
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        fig3 = px.line(
            df, x="Date", y="Calories",
            title="Calories Trend"
        )
        fig3.add_hline(y=DAILY_CAL_TARGET, line_dash="dash")
        st.plotly_chart(fig3, use_container_width=True)

    # Lifestyle
    st.markdown("## 🚶 Lifestyle Metrics")

    c3, c4 = st.columns(2)

    with c3:
        fig4 = px.line(df, x="Date", y="Steps", title="Daily Steps")
        fig4.add_hline(y=8000, line_dash="dash")
        st.plotly_chart(fig4, use_container_width=True)

    with c4:
        fig5 = px.line(df, x="Date", y="Water", title="Water Intake")
        fig5.add_hline(y=3.5, line_dash="dash")
        st.plotly_chart(fig5, use_container_width=True)

# -------------------------------
# DAILY SCORECARD
# -------------------------------
if len(df) > 0:
    st.markdown("## 🎯 Today's Score")

    score = 0
    if latest["Calories"] <= DAILY_CAL_TARGET: score += 20
    if latest["Protein"] >= DAILY_PROTEIN_TARGET: score += 20
    if latest["Steps"] >= 8000: score += 20
    if latest["Water"] >= 3.5: score += 20
    if latest["Workout"] == "Yes": score += 20

    st.progress(score / 100)
    st.write(f"Daily Discipline Score: **{score}/100**")

# -------------------------------
# DATA TABLE
# -------------------------------
st.markdown("## 📋 Full Tracker Data")
st.dataframe(df, use_container_width=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Stay consistent for 100 days. Results are inevitable.")
