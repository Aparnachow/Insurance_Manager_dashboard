import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.title("📅 PMPM (Per Member Per Month) Dashboard")

data_path = "data/cleaned_claims_full.csv"
if not os.path.exists(data_path):
    st.error("❌ Data file missing.")
    st.stop()

df = pd.read_csv(data_path)
df["ENCOUNTER_DATE"] = pd.to_datetime(df["ENCOUNTER_DATE"], errors="coerce")
df["MONTH"] = df["ENCOUNTER_DATE"].dt.to_period("M").astype(str)

# Unique patients per month
members = df.groupby("MONTH")["PATIENT"].nunique().reset_index()
members.columns = ["MONTH", "MemberCount"]

# Monthly cost
monthly_cost = df.groupby("MONTH")["TOTAL_CLAIM_COST"].sum().reset_index()

# PMPM
pmpm = monthly_cost.merge(members, on="MONTH")
pmpm["PMPM"] = pmpm["TOTAL_CLAIM_COST"] / pmpm["MemberCount"]

st.header("1️⃣ PMPM Trend")
fig = px.line(pmpm, x="MONTH", y="PMPM", title="PMPM Over Time")
st.plotly_chart(fig, use_container_width=True)

st.header("2️⃣ Monthly Member Count")
fig2 = px.bar(pmpm, x="MONTH", y="MemberCount", title="Members Per Month")
st.plotly_chart(fig2, use_container_width=True)

st.header("3️⃣ Total Monthly Claim Cost")
fig3 = px.bar(pmpm, x="MONTH", y="TOTAL_CLAIM_COST", title="Total Claim Cost Per Month")
st.plotly_chart(fig3, use_container_width=True)
