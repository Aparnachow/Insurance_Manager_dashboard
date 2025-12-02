import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.title("⚠️ High-Risk Patient Identification")

data_path = "data/cleaned_claims_full.csv"
if not os.path.exists(data_path):
    st.error("❌ Data file missing.")
    st.stop()

df = pd.read_csv(data_path)

# Risk Score = Cost + Dialysis + Diabetes + Age
df["RiskScore"] = (
    df["TOTAL_CLAIM_COST"].rank(pct=True) +
    df["IsDiabetes"] * 0.5 +
    df["IsDialysis"] * 0.8 +
    (df["AGE"] / df["AGE"].max())
)

st.header("1️⃣ Top 20 High-Risk Patients")
top_risk = df.sort_values("RiskScore", ascending=False).head(20)
st.dataframe(top_risk)

fig = px.bar(top_risk, x="PATIENT", y="RiskScore", color="RiskScore",
             title="Top High-Risk Patients")
st.plotly_chart(fig, use_container_width=True)

# Age vs Risk
st.header("2️⃣ Age vs Risk Scatter")
fig2 = px.scatter(df, x="AGE", y="RiskScore", color="IsDiabetes",
                  title="Risk Score by Age")
st.plotly_chart(fig2, use_container_width=True)
