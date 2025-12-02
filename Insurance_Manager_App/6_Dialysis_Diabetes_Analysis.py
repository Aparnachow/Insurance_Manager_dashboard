import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.title("🩺 Dialysis & Diabetes — Condition Analysis")

# ------------------------------
# LOAD DATA
# ------------------------------
data_path = "data/cleaned_claims_full.csv"

if os.path.exists(data_path):
    df = pd.read_csv(data_path)
else:
    st.error("❌ cleaned_claims_full.csv not found!")
    st.stop()

# DATE PROCESSING
df["ENCOUNTER_DATE"] = pd.to_datetime(df["ENCOUNTER_DATE"], errors="coerce")
df["MONTH"] = df["ENCOUNTER_DATE"].dt.to_period("M").astype(str)

# ------------------------------
# 1️⃣ TOTAL PATIENT COUNT
# ------------------------------
st.header("1️⃣ Total Patients with Diabetes & Dialysis")

diabetes_patients = df[df["IsDiabetes"] == 1]["PATIENT"].nunique()
dialysis_patients = df[df["IsDialysis"] == 1]["PATIENT"].nunique()

col1, col2 = st.columns(2)

col1.metric("🩸 Diabetes Patients", diabetes_patients)
col2.metric("💉 Dialysis Patients", dialysis_patients)

# ------------------------------
# 2️⃣ TOTAL CLAIM COST COMPARISON
# ------------------------------
st.header("2️⃣ Total Claim Cost — Diabetes vs Dialysis")

cost_compare = pd.DataFrame({
    "Condition": ["Diabetes", "Dialysis"],
    "Total Claim Cost": [
        df[df["IsDiabetes"] == 1]["TOTAL_CLAIM_COST"].sum(),
        df[df["IsDialysis"] == 1]["TOTAL_CLAIM_COST"].sum()
    ]
})

fig_cost = px.bar(
    cost_compare,
    x="Condition",
    y="Total Claim Cost",
    title="Total Claim Cost by Condition",
    color="Condition",
    text_auto=True
)

st.plotly_chart(fig_cost, use_container_width=True)
st.dataframe(cost_compare)

# ------------------------------
# 3️⃣ MONTHLY COST TREND
# ------------------------------
st.header("3️⃣ Monthly Trend — Diabetes vs Dialysis")

monthly_trend = df.groupby(["MONTH"]).agg(
    Diabetes_Cost=("TOTAL_CLAIM_COST", lambda x: x[df["IsDiabetes"] == 1].sum()),
    Dialysis_Cost=("TOTAL_CLAIM_COST", lambda x: x[df["IsDialysis"] == 1].sum())
).reset_index()

fig_trend = px.line(
    monthly_trend,
    x="MONTH",
    y=["Diabetes_Cost", "Dialysis_Cost"],
    title="Monthly Claim Cost Trend"
)

st.plotly_chart(fig_trend, use_container_width=True)
st.dataframe(monthly_trend)

# ------------------------------
# 4️⃣ AGE DISTRIBUTION
# ------------------------------
st.header("4️⃣ Age Distribution")

age_df = df[df["IsDiabetes"] + df["IsDialysis"] > 0]

fig_age = px.histogram(
    age_df,
    x="AGE",
    color=age_df["IsDiabetes"].apply(lambda x: "Diabetes" if x == 1 else "Dialysis"),
    title="Age Distribution of Patients"
)

st.plotly_chart(fig_age, use_container_width=True)

# ------------------------------
# 5️⃣ CITY-WISE DISTRIBUTION
# ------------------------------
st.header("5️⃣ City-wise Condition Spread")

city_df = df.groupby("CITY").agg(
    Diabetes=("IsDiabetes", "sum"),
    Dialysis=("IsDialysis", "sum")
).reset_index()

fig_city = px.bar(
    city_df,
    x="CITY",
    y=["Diabetes", "Dialysis"],
    title="City-wise Distribution"
)

st.plotly_chart(fig_city, use_container_width=True)
st.dataframe(city_df)

# ------------------------------
# 6️⃣ PATIENTS WITH BOTH CONDITIONS
# ------------------------------
st.header("6️⃣ Patients Having Both Diabetes & Dialysis")

both = df[(df["IsDiabetes"] == 1) & (df["IsDialysis"] == 1)]

st.metric("Count of Patients with Both Conditions", both["PATIENT"].nunique())
st.dataframe(both.head())
