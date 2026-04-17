# app_final.py
# FINAL VERSION
# Run: streamlit run app_final.py

import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.graph_objects as go

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Final Fat Loss Command Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CSV_FILE = "fat_loss_final.csv"

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

# =====================================================
# STYLE
# =====================================================
st.markdown("""
<style>
.block-container{
    padding-top:1rem;
    padding-bottom:2rem;
}
.big{
    font-size:34px;
    font-weight:800;
    color:#22c55e;
}
.small{
    color:#94a3b8;
}
thead tr th{
    text-align:center !important;
}
tbody tr td{
    text-align:center !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# FILE FUNCTIONS
# =====================================================
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
        pd.DataFrame(columns=cols).to_csv(CSV_FILE,index=False)

def load():
    return pd.read_csv(CSV_FILE)

def save(df):
    df.to_csv(CSV_FILE,index=False)

def target_weight(day):
    per_day = (START_WEIGHT - TARGET_WEIGHT) / TOTAL_DAYS
    return round(START_WEIGHT - (per_day * day),2)

def tick(actual,target,lower_better=False):
    if lower_better:
        return "✅" if actual <= target else "❌"
    return "✅" if actual >= target else "❌"

# =====================================================
# INIT
# =====================================================
init_file()
df = load()

# =====================================================
# HEADER
# =====================================================
st.markdown("<div class='big'>🎯 Final Fat Loss Command Center</div>", unsafe_allow_html=True)
st.markdown("<div class='small'>14 KG / 100 Day Challenge • Precision Dashboard</div>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard","➕ Add Entry","📜 History"])

# =====================================================
# ADD ENTRY
# =====================================================
with tab2:

    st.subheader("➕ Add Daily Entry")

    with st.form("entry_form"):

        log_date = st.date_input("Date", date.today())
        weight = st.number_input("Weight",40.0,200.0,88.0)

        c1,c2 = st.columns(2)

        with c1:
            st.markdown("### Breakfast")
            bc = st.number_input("B Calories",0,2000,400)
            bp = st.number_input("B Protein",0,300,35)
            bcarb = st.number_input("B Carbs",0,300,25)
            bf = st.number_input("B Fat",0,200,15)

            st.markdown("### Lunch")
            lc = st.number_input("L Calories",0,2000,650)
            lp = st.number_input("L Protein",0,300,45)
            lcarb = st.number_input("L Carbs",0,300,45)
            lf = st.number_input("L Fat",0,200,20)

        with c2:
            st.markdown("### Dinner")
            dc = st.number_input("D Calories",0,2000,550)
            dp = st.number_input("D Protein",0,300,45)
            dcarb = st.number_input("D Carbs",0,300,30)
            dfat = st.number_input("D Fat",0,200,18)

            st.markdown("### Other")
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

        workout = st.selectbox("Workout",["Yes","No"])
        notes = st.text_input("Notes")

        submit = st.form_submit_button("🚀 Save Entry")

        if submit:
            row = pd.DataFrame([{
                "Date":log_date,"Weight":weight,

                "B_Cal":bc,"B_Pro":bp,"B_Carb":bcarb,"B_Fat":bf,
                "L_Cal":lc,"L_Pro":lp,"L_Carb":lcarb,"L_Fat":lf,
                "D_Cal":dc,"D_Pro":dp,"D_Carb":dcarb,"D_Fat":dfat,
                "O_Cal":oc,"O_Pro":op,"O_Carb":ocarb,"O_Fat":of,

                "Water":water,"Steps":steps,
                "Workout":workout,"Sleep":sleep,"Notes":notes
            }])

            df = pd.concat([df,row],ignore_index=True)
            df.drop_duplicates(subset=["Date"],keep="last",inplace=True)
            save(df)
            st.success("Saved Successfully!")

# =====================================================
# PROCESS
# =====================================================
df = load()

if len(df) > 0:

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Day"] = range(1,len(df)+1)

    df["Calories"] = df["B_Cal"]+df["L_Cal"]+df["D_Cal"]+df["O_Cal"]
    df["Protein"] = df["B_Pro"]+df["L_Pro"]+df["D_Pro"]+df["O_Pro"]

    latest = df.iloc[-1]

# =====================================================
# DASHBOARD
# =====================================================
with tab1:

    if len(df)==0:
        st.info("Add first entry.")
    else:

        day = int(latest["Day"])
        target_today = target_weight(day)
        current = float(latest["Weight"])

        gap = round(current - target_today,2)
        lost = round(START_WEIGHT-current,2)

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("⚖️ Weight", f"{current} kg")
        c2.metric("🎯 Target Today", f"{target_today} kg")
        c3.metric("🔥 Lost", f"{lost} kg")
        c4.metric("📅 Day", f"{day}/100")

        if gap <= 0:
            st.success(f"✅ Ahead / On Track by {abs(gap)} kg")
        else:
            st.error(f"❌ Behind by {gap} kg")

        st.markdown("---")

        st.subheader("🍽️ Meal Target vs Actual")

        table = pd.DataFrame({
            "Meal":["Breakfast","Lunch","Dinner","Other"],

            "Target Cal":[400,650,550,250],
            "Actual Cal":[latest["B_Cal"],latest["L_Cal"],latest["D_Cal"],latest["O_Cal"]],
            "Cal Status":[
                tick(latest["B_Cal"],400,True),
                tick(latest["L_Cal"],650,True),
                tick(latest["D_Cal"],550,True),
                tick(latest["O_Cal"],250,True),
            ],

            "Target Protein":[35,45,45,25],
            "Actual Protein":[latest["B_Pro"],latest["L_Pro"],latest["D_Pro"],latest["O_Pro"]],
            "Protein Status":[
                tick(latest["B_Pro"],35),
                tick(latest["L_Pro"],45),
                tick(latest["D_Pro"],45),
                tick(latest["O_Pro"],25),
            ],

            "Target Carbs":[25,45,30,15],
            "Actual Carbs":[latest["B_Carb"],latest["L_Carb"],latest["D_Carb"],latest["O_Carb"]],

            "Target Fat":[15,20,18,8],
            "Actual Fat":[latest["B_Fat"],latest["L_Fat"],latest["D_Fat"],latest["O_Fat"]],
        })

        st.dataframe(table, use_container_width=True)

        st.markdown("---")

        st.subheader("📊 Daily Total Score")

        c5,c6,c7,c8 = st.columns(4)

        c5.metric("Calories", f"{int(latest['Calories'])}/{TOTAL_CAL_TARGET}")
        c6.metric("Protein", f"{int(latest['Protein'])}/{TOTAL_PRO_TARGET}g")
        c7.metric("Steps", f"{int(latest['Steps'])}/{STEP_TARGET}")
        c8.metric("Water", f"{latest['Water']}/{WATER_TARGET}L")

        st.markdown("---")

        st.subheader("📉 Weight Progress")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Weight"],
            mode="lines+markers",
            name="Actual Weight"
        ))

        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=[target_weight(x) for x in df["Day"]],
            mode="lines",
            name="Target Weight"
        ))

        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        st.subheader("🧠 Recommendation")

        if gap > 0:
            st.warning(
                f"You are behind by {gap} kg. "
                f"Suggested today: +2500 steps OR -180 kcal OR 20 min cardio."
            )
        else:
            st.success("Maintain current pace. You are on track.")

# =====================================================
# HISTORY
# =====================================================
with tab3:

    if len(df)==0:
        st.info("No history.")
    else:
        st.dataframe(df, use_container_width=True)
