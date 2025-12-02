import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.title("🏦 Payer Analytics Dashboard")

# --------------------------------------
# LOAD DATA
# --------------------------------------
data_path = "data/cleaned_claims_full.csv"

if os.path.exists(data_path):
    df = pd.read_csv(data_path)
else:
    st.error("❌ cleaned_claims_full.csv not found!")
    st.stop()

# --------------------------------------
# DATE PROCESSING
# --------------------------------------
if "ENCOUNTER_DATE" in df.columns:
    df["ENCOUNTER_DATE"] = pd.to_datetime(df["ENCOUNTER_DATE"], errors="coerce")
    df["YEAR"] = df["ENCOUNTER_DATE"].dt.year
    df["MONTH"] = df["ENCOUNTER_DATE"].dt.to_period("M").astype(str)

# --------------------------------------
# CREATE CLAIM_STATUS
# --------------------------------------
if "PAYER_NAME" in df.columns:
    df["CLAIM_STATUS"] = df["PAYER_NAME"].apply(
        lambda x: "Rejected" if str(x).strip().upper() == "NO_INSURANCE" else "Accepted"
    )
else:
    st.warning("⚠️ PAYER_NAME column missing — cannot create CLAIM_STATUS.")


# --------------------------------------
# 1️⃣ WHICH PAYER PAYS THE MOST?
# --------------------------------------
st.header("1️⃣ Total Claim Amount by Payer")

payer_cost = df.groupby("PAYER")["TOTAL_CLAIM_COST"].sum().reset_index()
payer_cost = payer_cost.sort_values("TOTAL_CLAIM_COST", ascending=False)

fig1 = px.bar(
    payer_cost,
    x="PAYER",
    y="TOTAL_CLAIM_COST",
    title="Total Claim Cost by Payer",
    labels={"TOTAL_CLAIM_COST": "Total Claim Cost"}
)
st.plotly_chart(fig1, use_container_width=True)
st.dataframe(payer_cost)

# --------------------------------------
# 2️⃣ CLAIM ACCEPTANCE RATE BY PAYER
# --------------------------------------
st.header("2️⃣ Claim Acceptance Rate by Payer")

if "CLAIM_STATUS" in df.columns:
    accept_rate = df.groupby("PAYER")["CLAIM_STATUS"].apply(
        lambda x: (x == "Accepted").mean()
    ).reset_index()
    accept_rate.rename(columns={"CLAIM_STATUS": "AcceptanceRate"}, inplace=True)

    fig2 = px.bar(
        accept_rate,
        x="PAYER",
        y="AcceptanceRate",
        title="Acceptance Rate (%) by Payer"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(accept_rate)
else:
    st.warning("⚠ CLAIM_STATUS column missing — cannot calculate acceptance rate.")

# --------------------------------------
# 3️⃣ AVERAGE CLAIM COST PER PAYER
# --------------------------------------
st.header("3️⃣ Average Claim Cost per Payer")

avg_cost = df.groupby("PAYER")["TOTAL_CLAIM_COST"].mean().reset_index()

fig3 = px.bar(
    avg_cost,
    x="PAYER",
    y="TOTAL_CLAIM_COST",
    title="Average Claim Cost per Payer",
    labels={"TOTAL_CLAIM_COST": "Average Claim Cost"}
)
st.plotly_chart(fig3, use_container_width=True)
st.dataframe(avg_cost)

# --------------------------------------
# 4️⃣ RANK PAYERS (HIGH → LOW CLAIM COST)
# --------------------------------------
st.header("4️⃣ Payer Ranking by Total Claim Cost")

rank_table = payer_cost.copy()
rank_table["Rank"] = rank_table["TOTAL_CLAIM_COST"].rank(ascending=False)

st.dataframe(rank_table)

# --------------------------------------
# 5️⃣ ACCEPTANCE RATE TREND (MONTHLY)
# --------------------------------------
st.header("5️⃣ Monthly Acceptance Rate Trend by Payer")

if "CLAIM_STATUS" in df.columns and "MONTH" in df.columns:
    trend = df.groupby(["PAYER", "MONTH"])["CLAIM_STATUS"].apply(
        lambda x: (x == "Accepted").mean()
    ).reset_index()
    trend.rename(columns={"CLAIM_STATUS": "AcceptanceRate"}, inplace=True)

    fig4 = px.line(
        trend,
        x="MONTH",
        y="AcceptanceRate",
        color="PAYER",
        title="Monthly Acceptance Rate Trend"
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.dataframe(trend)

# --------------------------------------
# 6️⃣ ACCEPTANCE RATE PER YEAR
# --------------------------------------
st.header("6️⃣ Yearly Claim Acceptance Rate")

if "CLAIM_STATUS" in df.columns:
    yearly_acceptance = df.groupby("YEAR")["CLAIM_STATUS"].apply(
        lambda x: (x == "Accepted").mean()
    ).reset_index()
    yearly_acceptance.rename(columns={"CLAIM_STATUS": "AcceptanceRate"}, inplace=True)

    fig_year = px.bar(
        yearly_acceptance,
        x="YEAR",
        y="AcceptanceRate",
        title="Yearly Claim Acceptance Rate"
    )
    st.plotly_chart(fig_year, use_container_width=True)
    st.dataframe(yearly_acceptance)

# --------------------------------------
# 7️⃣ CLAIM TREND ANALYSIS (MONTHLY)
# --------------------------------------
st.header("7️⃣ Monthly Claim Cost Trend Over Time")

monthly_trend = df.groupby("MONTH")["TOTAL_CLAIM_COST"].sum().reset_index()

fig_month = px.line(
    monthly_trend,
    x="MONTH",
    y="TOTAL_CLAIM_COST",
    title="Monthly Claim Cost Trend",
    labels={"TOTAL_CLAIM_COST": "Total Claim Cost"}
)
st.plotly_chart(fig_month, use_container_width=True)
st.dataframe(monthly_trend)

# --------------------------------------
# 8️⃣ CLAIM TREND ANALYSIS (YEARLY)
# --------------------------------------
st.header("8️⃣ Yearly Claim Cost Trend Over Time")

yearly_trend = df.groupby("YEAR")["TOTAL_CLAIM_COST"].sum().reset_index()

fig_year2 = px.line(
    yearly_trend,
    x="YEAR",
    y="TOTAL_CLAIM_COST",
    title="Yearly Claim Cost Trend",
    labels={"TOTAL_CLAIM_COST": "Total Claim Cost"}
)
st.plotly_chart(fig_year2, use_container_width=True)
st.dataframe(yearly_trend)
