# app_v4.py
# Run: streamlit run app_v4.py

import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.graph_objects as go
import plotly.express as px

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(
    page_title="V4 Elite Fat Loss Command Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CSV_FILE = "fat_loss_tracker_v4.csv"

START_WEIGHT = 88.0
TARGET_WEIGHT = 74.0
TOTAL_DAYS = 100

TOTAL_CAL_TARGET = 1850
TOTAL_PRO_TARGET = 150
TOTAL_CARB_TARGET = 115
TOTAL_FAT_TARGET = 61

STEP_TARGET = 10000
WATER_TARGET = 3.5

MEALS = {
    "Breakfast": {"cal": 400, "pro": 35, "carb": 25, "fat": 15},
    "Lunch": {"cal": 650, "pro": 45, "carb": 45, "fat": 20},
    "Dinner": {"cal": 550, "pro": 45, "carb": 30, "fat": 18},
    "Other": {"cal": 250, "pro": 25, "carb": 15, "fat": 8},
}

# ======================================================
# STYLE
# ======================================================
st.markdown("""
<style>
.block-container{padding-top:1rem;padding-bottom:2rem;}
.card{
    background:#111827;
    border:1px solid #1f2937;
    padding:16px;
    border-radius:18px;
}
.big{font-size:34px;font-weight:800;color:#22c55e;}
.small{color:#94a3b8;}
.good{color:#22c55e;font-weight:700;}
.bad{color:#ef4444;font-weight:700;}
.warn{color:#f59e0b;font-weight:700;}
</style>
""", unsafe_allow_html=True)

# ======================================================
# HELPERS
# ======================================================
def init_file():
    if not os.path.exists(CSV_FILE):
        cols = [
            "Date","Weight",
            "B_Cal","B_Pro","B_Carb","B_Fat",
            "L_Cal","L_Pro","L_Carb","L_Fat",
            "D_Cal","D_Pro","D_Carb","D_Fat",
            "O_Cal","O_Pro","O_Carb","O_Fat",
            "Water","Steps","Workout","Sleep","Notes"
        ]
        pd.DataFrame(columns=cols).to_csv(CSV_FILE, index=False)

def load():
    return pd.read_csv(CSV_FILE)

def save(df):
    df.to_csv(CSV_FILE, index=False)

def target_weight_for_day(day):
    per_day = (START_WEIGHT - TARGET_WEIGHT) / TOTAL_DAYS
    return round(START_WEIGHT - (per_day * day), 2)

def status_color(diff):
    if diff <= 0:
        return "good"
    elif diff <= 0.5:
        return "warn"
    return "bad"

def show_compare(metric, target, actual, unit=""):
    diff = actual - target
    icon = "✅" if actual <= target and metric=="Calories" else "✅" if actual >= target else "❌"
    st.write(f"**{metric}:** Target {target}{unit} | Actual {actual}{unit} {icon}")

# ======================================================
# INIT
# ======================================================
init_file()
df = load()

# ======================================================
# HEADER
# ======================================================
st.markdown("<div class='big'>🎯 V4 Elite Fat Loss Command Center</div>", unsafe_allow_html=True)
st.markdown("<div class='small'>14 kg in 100 Days | Precision Tracker | Decision Dashboard</div>", unsafe_allow_html=True)
st.markdown("---")

tabs = st.tabs(["📊 Dashboard", "➕ Add Entry", "📜 History"])

# ======================================================
# ADD ENTRY TAB
# ======================================================
with tabs[1]:
    st.subheader("➕ Add Daily Entry")

    with st.form("entry"):
        log_date = st.date_input("Date", date.today())
        weight = st.number_input("Weight (kg)", 40.0, 200.0, 88.0)

        c1,c2 = st.columns(2)

        with c1:
            st.markdown("### 🍳 Breakfast")
            bc = st.number_input("B Calories",0,2000,400)
            bp = st.number_input("B Protein",0,300,35)
            bcarb = st.number_input("B Carbs",0,300,25)
            bf = st.number_input("B Fat",0,200,15)

            st.markdown("### 🍛 Lunch")
            lc = st.number_input("L Calories",0,2000,650)
            lp = st.number_input("L Protein",0,300,45)
            lcarb = st.number_input("L Carbs",0,300,45)
            lf = st.number_input("L Fat",0,200,20)

        with c2:
            st.markdown("### 🍲 Dinner")
            dc = st.number_input("D Calories",0,2000,550)
            dp = st.number_input("D Protein",0,300,45)
            dcarb = st.number_input("D Carbs",0,300,30)
            dfat = st.number_input("D Fat",0,200,18)

            st.markdown("### 🍎 Other Meals")
            oc = st.number_input("O Calories",0,2000,250)
            op = st.number_input("O Protein",0,300,25)
            ocarb = st.number_input("O Carbs",0,300,15)
            of = st.number_input("O Fat",0,200,8)

        c3,c4,c5 = st.columns(3)
        with c3:
            water = st.number_input("Water (L)",0.0,10.0,3.5)
        with c4:
            steps = st.number_input("Steps",0,50000,10000)
        with c5:
            sleep = st.number_input("Sleep",0.0,12.0,7.0)

        workout = st.selectbox("Workout Done?",["Yes","No"])
        notes = st.text_input("Notes")

        if st.form_submit_button("🚀 Save Entry"):
            row = pd.DataFrame([{
                "Date":log_date,"Weight":weight,
                "B_Cal":bc,"B_Pro":bp,"B_Carb":bcarb,"B_Fat":bf,
                "L_Cal":lc,"L_Pro":lp,"L_Carb":lcarb,"L_Fat":lf,
                "D_Cal":dc,"D_Pro":dp,"D_Carb":dcarb,"D_Fat":dfat,
                "O_Cal":oc,"O_Pro":op,"O_Carb":ocarb,"O_Fat":of,
                "Water":water,"Steps":steps,"Workout":workout,"Sleep":sleep,"Notes":notes
            }])

            df = pd.concat([df,row], ignore_index=True)
            df.drop_duplicates(subset=["Date"], keep="last", inplace=True)
            save(df)
            st.success("Saved Successfully!")

# ======================================================
# PROCESS DATA
# ======================================================
df = load()

if len(df) > 0:
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Day"] = range(1, len(df)+1)

    df["Calories"] = df["B_Cal"]+df["L_Cal"]+df["D_Cal"]+df["O_Cal"]
    df["Protein"] = df["B_Pro"]+df["L_Pro"]+df["D_Pro"]+df["O_Pro"]
    df["Carbs"] = df["B_Carb"]+df["L_Carb"]+df["D_Carb"]+df["O_Carb"]
    df["Fat"] = df["B_Fat"]+df["L_Fat"]+df["D_Fat"]+df["O_Fat"]

    latest = df.iloc[-1]

# ======================================================
# DASHBOARD
# ======================================================
with tabs[0]:
    if len(df) == 0:
        st.info("Add your first entry.")
    else:
        today = int(latest["Day"])
        target_today = target_weight_for_day(today)
        actual = float(latest["Weight"])
        diff = round(actual - target_today,2)
        lost = round(START_WEIGHT - actual,2)
        should_lost = round(START_WEIGHT - target_today,2)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("⚖️ Current Weight", f"{actual} kg")
        c2.metric("🎯 Target Today", f"{target_today} kg")
        c3.metric("🔥 Actual Lost", f"{lost} kg")
        c4.metric("📅 Day", f"{today}/100")

        cls = status_color(diff)
        st.markdown(f"<h3 class='{cls}'>Progress Gap: {diff:+} kg {'(Ahead)' if diff<=0 else '(Behind)'}</h3>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🍽️ Meal Target vs Actual")

        meal_cols = st.columns(4)

        meal_data = {
            "Breakfast":[latest["B_Cal"], latest["B_Pro"], latest["B_Carb"], latest["B_Fat"]],
            "Lunch":[latest["L_Cal"], latest["L_Pro"], latest["L_Carb"], latest["L_Fat"]],
            "Dinner":[latest["D_Cal"], latest["D_Pro"], latest["D_Carb"], latest["D_Fat"]],
            "Other":[latest["O_Cal"], latest["O_Pro"], latest["O_Carb"], latest["O_Fat"]],
        }

        for idx, meal in enumerate(["Breakfast","Lunch","Dinner","Other"]):
            with meal_cols[idx]:
                st.markdown(f"### {meal}")
                show_compare("Calories", MEALS[meal]["cal"], meal_data[meal][0])
                show_compare("Protein", MEALS[meal]["pro"], meal_data[meal][1], "g")
                show_compare("Carbs", MEALS[meal]["carb"], meal_data[meal][2], "g")
                show_compare("Fat", MEALS[meal]["fat"], meal_data[meal][3], "g")

        st.markdown("---")
        st.subheader("📊 Daily Total Targets")

        c5,c6,c7,c8 = st.columns(4)
        c5.metric("Calories", f"{int(latest['Calories'])}/{TOTAL_CAL_TARGET}")
        c6.metric("Protein", f"{int(latest['Protein'])}/{TOTAL_PRO_TARGET} g")
        c7.metric("Steps", f"{int(latest['Steps'])}/{STEP_TARGET}")
        c8.metric("Water", f"{latest['Water']}/{WATER_TARGET} L")

        st.markdown("---")
        st.subheader("📉 Weight Progress")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Weight"],
            mode="lines+markers",
            name="Actual"
        ))
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=[target_weight_for_day(x) for x in df["Day"]],
            mode="lines",
            name="Target"
        ))
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🧠 Recommendation Engine")

        if diff > 0:
            st.warning(
                f"You are behind by {diff} kg. "
                f"Suggested today: +2500 steps OR reduce 180 kcal OR add 20 min cardio."
            )
        else:
            st.success("You are on track or ahead. Maintain consistency.")

# ======================================================
# HISTORY
# ======================================================
with tabs[2]:
    if len(df) == 0:
        st.info("No entries yet.")
    else:
        st.dataframe(df, use_container_width=True)
