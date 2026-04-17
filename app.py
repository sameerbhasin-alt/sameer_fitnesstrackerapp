# app_v3.py
# Run: streamlit run app_v3.py

import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px
import plotly.graph_objects as go

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="100 Day Fat Loss Quest",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CSV_FILE = "fat_loss_tracker_v3.csv"

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
.block-container{
    padding-top:1rem;
    padding-bottom:2rem;
}
.metric-card{
    background: rgba(255,255,255,0.04);
    padding:18px;
    border-radius:18px;
    border:1px solid rgba(255,255,255,0.08);
}
.big{
    font-size:34px;
    font-weight:800;
}
.green{
    color:#22c55e;
}
.small{
    color:#94a3b8;
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
        pd.DataFrame(columns=cols).to_csv(CSV_FILE, index=False)

def load_data():
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def expected_weight(day):
    per_day = (START_WEIGHT - TARGET_WEIGHT) / TOTAL_DAYS
    return round(START_WEIGHT - (day * per_day), 2)

init_file()
df = load_data()

# ---------------- HEADER ----------------
st.markdown("<div class='big green'>🎮 100 Day Fat Loss Quest</div>", unsafe_allow_html=True)
st.markdown("<div class='small'>Track meals. Gain XP. Lose fat. Build discipline.</div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add Daily Entry", "📜 History"])

# ==================================================
# TAB 2 - ENTRY FORM
# ==================================================
with tab2:

    st.subheader("➕ Add Daily Entry")

    with st.form("entry_form"):
        log_date = st.date_input("Date", date.today())
        weight = st.number_input("Weight (kg)", 40.0, 200.0, 88.0)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### 🍳 Breakfast")
            bc = st.number_input("Breakfast Calories",0,2000,400)
            bp = st.number_input("Breakfast Protein",0,200,30)
            bcarb = st.number_input("Breakfast Carbs",0,300,25)
            bf = st.number_input("Breakfast Fat",0,100,15)

            st.markdown("### 🍛 Lunch")
            lc = st.number_input("Lunch Calories",0,2000,600)
            lp = st.number_input("Lunch Protein",0,200,45)
            lcarb = st.number_input("Lunch Carbs",0,300,40)
            lf = st.number_input("Lunch Fat",0,100,18)

        with c2:
            st.markdown("### 🍲 Dinner")
            dc = st.number_input("Dinner Calories",0,2000,550)
            dp = st.number_input("Dinner Protein",0,200,45)
            dcarb = st.number_input("Dinner Carbs",0,300,30)
            dfat = st.number_input("Dinner Fat",0,100,18)

            st.markdown("### 🍎 Other Meals")
            oc = st.number_input("Other Calories",0,2000,250)
            op = st.number_input("Other Protein",0,200,25)
            ocarb = st.number_input("Other Carbs",0,300,15)
            of = st.number_input("Other Fat",0,100,8)

        st.markdown("### 💧 Lifestyle")

        c3, c4, c5 = st.columns(3)

        with c3:
            water = st.number_input("Water (L)",0.0,10.0,3.5)

        with c4:
            steps = st.number_input("Steps",0,50000,8000)

        with c5:
            sleep = st.number_input("Sleep Hours",0.0,12.0,7.0)

        workout = st.selectbox("Workout Done?",["Yes","No"])
        notes = st.text_input("Notes")

        submitted = st.form_submit_button("🚀 Save Progress")

        if submitted:
            row = pd.DataFrame([{
                "Date":log_date,
                "Weight":weight,

                "B_Cal":bc,"B_Protein":bp,"B_Carb":bcarb,"B_Fat":bf,
                "L_Cal":lc,"L_Protein":lp,"L_Carb":lcarb,"L_Fat":lf,
                "D_Cal":dc,"D_Protein":dp,"D_Carb":dcarb,"D_Fat":dfat,
                "O_Cal":oc,"O_Protein":op,"O_Carb":ocarb,"O_Fat":of,

                "Water":water,
                "Steps":steps,
                "Workout":workout,
                "Sleep":sleep,
                "Notes":notes
            }])

            df = pd.concat([df,row],ignore_index=True)
            df.drop_duplicates(subset=["Date"], keep="last", inplace=True)
            save_data(df)
            st.success("✅ Progress Saved!")

# ==================================================
# PROCESS DATA
# ==================================================
df = load_data()

if len(df) > 0:
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Day"] = range(1, len(df)+1)

    df["Expected Weight"] = df["Day"].apply(expected_weight)

    df["Calories"] = df["B_Cal"] + df["L_Cal"] + df["D_Cal"] + df["O_Cal"]
    df["Protein"] = df["B_Protein"] + df["L_Protein"] + df["D_Protein"] + df["O_Protein"]
    df["Carbs"] = df["B_Carb"] + df["L_Carb"] + df["D_Carb"] + df["O_Carb"]
    df["Fat"] = df["B_Fat"] + df["L_Fat"] + df["D_Fat"] + df["O_Fat"]

    latest = df.iloc[-1]

    # XP SYSTEM
    xp = 0
    if latest["Calories"] <= CAL_TARGET: xp += 25
    if latest["Protein"] >= PROTEIN_TARGET: xp += 25
    if latest["Steps"] >= STEP_TARGET: xp += 25
    if latest["Water"] >= WATER_TARGET: xp += 15
    if latest["Workout"] == "Yes": xp += 10

    level = int(len(df)/7) + 1

# ==================================================
# TAB 1 - DASHBOARD
# ==================================================
with tab1:

    if len(df) == 0:
        st.info("Add your first entry in Add Daily Entry tab.")
    else:
        c1,c2,c3,c4 = st.columns(4)

        c1.metric("⚖️ Weight", f"{latest['Weight']} kg")
        c2.metric("🔥 Lost", f"{round(START_WEIGHT-latest['Weight'],1)} kg")
        c3.metric("🎯 Level", level)
        c4.metric("⭐ XP", f"{xp}/100")

        st.progress(xp/100)

        st.markdown("### 🧭 Mission Progress")
        prog = len(df)/TOTAL_DAYS
        st.progress(prog)
        st.write(f"Day {len(df)} / {TOTAL_DAYS}")

        a,b = st.columns(2)

        with a:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["Weight"],
                mode="lines+markers", name="Actual"
            ))
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["Expected Weight"],
                mode="lines", name="Target"
            ))
            fig.update_layout(height=400, title="📉 Weight Journey")
            st.plotly_chart(fig, use_container_width=True)

        with b:
            meal = {
                "Breakfast": latest["B_Protein"],
                "Lunch": latest["L_Protein"],
                "Dinner": latest["D_Protein"],
                "Other": latest["O_Protein"]
            }
            fig2 = px.pie(
                values=list(meal.values()),
                names=list(meal.keys()),
                title="🍗 Protein by Meal"
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 🏆 Daily Scoreboard")

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

# ==================================================
# TAB 3 - HISTORY
# ==================================================
with tab3:

    if len(df) == 0:
        st.info("No history yet.")
    else:
        st.subheader("📜 Full Progress History")
        st.dataframe(df, use_container_width=True)
