# app_v2.py
# Run: streamlit run app_v2.py

import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.graph_objects as go
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Gamified Fat Loss Tracker", layout="wide")

CSV_FILE = "fat_loss_tracker_v2.csv"

START_WEIGHT = 88
TARGET_WEIGHT = 74
TOTAL_DAYS = 100

CAL_TARGET = 1850
PROTEIN_TARGET = 150
STEP_TARGET = 10000
WATER_TARGET = 3.5

# ---------------- STYLE ----------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#0f172a,#111827);
    color: white;
}
.metric-card {
    padding:18px;
    border-radius:18px;
    background: rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.08);
}
.big-title{
    font-size:38px;
    font-weight:800;
    color:#22c55e;
}
.small-muted{
    color:#cbd5e1;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FILE ----------------
def init_file():
    if not os.path.exists(CSV_FILE):
        cols = [
            "Date","Weight",

            "B_Cal","B_Protein","B_Carb","B_Fat",
            "L_Cal","L_Protein","L_Carb","L_Fat",
            "D_Cal","D_Protein","D_Carb","D_Fat",
            "O_Cal","O_Protein","O_Carb","O_Fat",

            "Water","Steps","Workout","Sleep","Notes"
        ]
        pd.DataFrame(columns=cols).to_csv(CSV_FILE,index=False)

def load():
    return pd.read_csv(CSV_FILE)

def save(df):
    df.to_csv(CSV_FILE,index=False)

def expected_weight(day):
    drop = (START_WEIGHT - TARGET_WEIGHT) / TOTAL_DAYS
    return round(START_WEIGHT - (drop * day),2)

init_file()
df = load()

# ---------------- HEADER ----------------
st.markdown("<div class='big-title'>🎮 100 Day Fat Loss Quest</div>", unsafe_allow_html=True)
st.markdown("<div class='small-muted'>Level up daily. Burn fat. Build discipline.</div>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📝 Daily Log")

log_date = st.sidebar.date_input("Date", date.today())
weight = st.sidebar.number_input("Weight", 40.0, 200.0, 88.0)

st.sidebar.markdown("## 🍳 Breakfast")
bc = st.sidebar.number_input("Breakfast Calories",0,2000,400)
bp = st.sidebar.number_input("Breakfast Protein",0,200,30)
bcarb = st.sidebar.number_input("Breakfast Carbs",0,300,25)
bf = st.sidebar.number_input("Breakfast Fat",0,100,15)

st.sidebar.markdown("## 🍛 Lunch")
lc = st.sidebar.number_input("Lunch Calories",0,2000,600)
lp = st.sidebar.number_input("Lunch Protein",0,200,45)
lcarb = st.sidebar.number_input("Lunch Carbs",0,300,40)
lf = st.sidebar.number_input("Lunch Fat",0,100,18)

st.sidebar.markdown("## 🍲 Dinner")
dc = st.sidebar.number_input("Dinner Calories",0,2000,550)
dp = st.sidebar.number_input("Dinner Protein",0,200,45)
dcarb = st.sidebar.number_input("Dinner Carbs",0,300,30)
dfat = st.sidebar.number_input("Dinner Fat",0,100,18)

st.sidebar.markdown("## 🍎 Other Meals")
oc = st.sidebar.number_input("Other Calories",0,2000,250)
op = st.sidebar.number_input("Other Protein",0,200,25)
ocarb = st.sidebar.number_input("Other Carbs",0,300,15)
of = st.sidebar.number_input("Other Fat",0,100,8)

water = st.sidebar.number_input("Water (L)",0.0,10.0,3.5)
steps = st.sidebar.number_input("Steps",0,50000,8000)
workout = st.sidebar.selectbox("Workout",["Yes","No"])
sleep = st.sidebar.number_input("Sleep Hours",0.0,12.0,7.0)
notes = st.sidebar.text_input("Notes")

if st.sidebar.button("🚀 Save Progress"):
    row = pd.DataFrame([{
        "Date":log_date,"Weight":weight,

        "B_Cal":bc,"B_Protein":bp,"B_Carb":bcarb,"B_Fat":bf,
        "L_Cal":lc,"L_Protein":lp,"L_Carb":lcarb,"L_Fat":lf,
        "D_Cal":dc,"D_Protein":dp,"D_Carb":dcarb,"D_Fat":dfat,
        "O_Cal":oc,"O_Protein":op,"O_Carb":ocarb,"O_Fat":of,

        "Water":water,"Steps":steps,"Workout":workout,"Sleep":sleep,"Notes":notes
    }])

    df = pd.concat([df,row],ignore_index=True)
    df.drop_duplicates(subset=["Date"],keep="last",inplace=True)
    save(df)
    st.sidebar.success("Saved!")

df = load()

# ---------------- PROCESS ----------------
if len(df) > 0:
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Day"] = range(1,len(df)+1)
    df["Expected Weight"] = df["Day"].apply(expected_weight)

    df["Calories"] = df["B_Cal"]+df["L_Cal"]+df["D_Cal"]+df["O_Cal"]
    df["Protein"] = df["B_Protein"]+df["L_Protein"]+df["D_Protein"]+df["O_Protein"]
    df["Carbs"] = df["B_Carb"]+df["L_Carb"]+df["D_Carb"]+df["O_Carb"]
    df["Fat"] = df["B_Fat"]+df["L_Fat"]+df["D_Fat"]+df["O_Fat"]

    latest = df.iloc[-1]

    # ---------------- XP SYSTEM ----------------
    xp = 0
    if latest["Calories"] <= CAL_TARGET: xp += 25
    if latest["Protein"] >= PROTEIN_TARGET: xp += 25
    if latest["Steps"] >= STEP_TARGET: xp += 25
    if latest["Water"] >= WATER_TARGET: xp += 15
    if latest["Workout"] == "Yes": xp += 10

    level = int(df.shape[0] / 7) + 1

    # ---------------- TOP METRICS ----------------
    c1,c2,c3,c4 = st.columns(4)

    c1.metric("⚖️ Weight", f"{latest['Weight']} kg")
    c2.metric("🔥 Total Lost", f"{round(START_WEIGHT-latest['Weight'],1)} kg")
    c3.metric("🎯 Level", level)
    c4.metric("⭐ XP Today", f"{xp}/100")

    st.progress(xp/100)

    # ---------------- QUEST STATUS ----------------
    st.markdown("## 🧭 Mission Progress")

    progress = len(df)/TOTAL_DAYS
    st.progress(progress)
    st.write(f"Day {len(df)} / {TOTAL_DAYS}")

    # ---------------- CHARTS ----------------
    col1,col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Weight"], mode="lines+markers", name="Actual"))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Expected Weight"], mode="lines", name="Target"))
        fig.update_layout(title="📉 Weight Journey", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        meal = {
            "Breakfast": latest["B_Protein"],
            "Lunch": latest["L_Protein"],
            "Dinner": latest["D_Protein"],
            "Other": latest["O_Protein"]
        }
        fig2 = px.pie(values=list(meal.values()), names=list(meal.keys()), title="🍗 Protein by Meal")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- SCOREBOARD ----------------
    st.markdown("## 🏆 Daily Scoreboard")

    score = pd.DataFrame({
        "Metric":["Calories","Protein","Steps","Water","Workout"],
        "Status":[
            "✅" if latest["Calories"] <= CAL_TARGET else "❌",
            "✅" if latest["Protein"] >= PROTEIN_TARGET else "❌",
            "✅" if latest["Steps"] >= STEP_TARGET else "❌",
            "✅" if latest["Water"] >= WATER_TARGET else "❌",
            "✅" if latest["Workout"]=="Yes" else "❌"
        ]
    })

    st.table(score)

    # ---------------- RAW DATA ----------------
    st.markdown("## 📜 Progress History")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Add your first entry from sidebar to begin the quest.")
