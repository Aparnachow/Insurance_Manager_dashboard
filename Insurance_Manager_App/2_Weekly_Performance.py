import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE TITLE
# ----------------------------
st.title("📊 Weekly Performance Overview")

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv("data/cleaned_claims_full.csv")

# Handle encounter/start date safely
if "ENCOUNTER_DATE" in df.columns:
    df["DATE"] = pd.to_datetime(df["ENCOUNTER_DATE"], errors="coerce")
elif "START" in df.columns:
    df["DATE"] = pd.to_datetime(df["START"], errors="coerce")
else:
    st.warning("⚠️ No encounter or start date column found in dataset.")
    df["DATE"] = pd.NaT

# Extract week and month
df["WEEK"] = df["DATE"].dt.isocalendar().week
df["YEAR"] = df["DATE"].dt.year
df["MONTH"] = df["DATE"].dt.to_period("M").astype(str)

# ----------------------------
# FILTERS
# ----------------------------
st.sidebar.header("🔍 Filters")
selected_year = st.sidebar.selectbox("Select Year:", sorted(df["YEAR"].dropna().unique()))
filtered_df = df[df["YEAR"] == selected_year]

# ----------------------------
# KPIs
# ----------------------------
weekly_summary = filtered_df.groupby("WEEK").agg({
    "TOTAL_CLAIM_COST": "sum",
    "IsDiabetes": "sum",
    "IsDialysis": "sum"
}).reset_index()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Cost", f"${filtered_df['TOTAL_CLAIM_COST'].sum():,.0f}")
col2.metric("📆 Weeks Covered", f"{weekly_summary['WEEK'].nunique()}")
col3.metric("🏥 Unique Patients", f"{filtered_df['PATIENT'].nunique():,}")

st.markdown("---")

# ----------------------------
# CHART 1: WEEKLY CLAIM COST
# ----------------------------
st.subheader(f"📈 Weekly Total Claim Cost — {selected_year}")
fig1 = px.line(
    weekly_summary,
    x="WEEK",
    y="TOTAL_CLAIM_COST",
    title="Weekly Total Claim Cost",
    markers=True,
    color_discrete_sequence=["#1565C0"]
)
st.plotly_chart(fig1, use_container_width=True)

# ----------------------------
# CHART 2: WEEKLY CONDITION TREND
# ----------------------------
st.subheader("🏥 Weekly Diabetes vs Dialysis Cases")
fig2 = px.bar(
    weekly_summary,
    x="WEEK",
    y=["IsDiabetes", "IsDialysis"],
    barmode="group",
    title="Weekly Chronic Condition Counts"
)
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# CHART 3: COST BY ORGANIZATION
# ----------------------------
if "ORGANIZATION" in df.columns:
    st.subheader("🏢 Top Organizations by Claim Cost")
    org_weekly = (
        filtered_df.groupby(["ORGANIZATION"])["TOTAL_CLAIM_COST"]
        .sum()
        .reset_index()
        .sort_values(by="TOTAL_CLAIM_COST", ascending=False)
        .head(10)
    )
    fig3 = px.bar(
        org_weekly,
        x="ORGANIZATION",
        y="TOTAL_CLAIM_COST",
        title="Top 10 Organizations by Claim Cost",
        color_discrete_sequence=["#42A5F5"]
    )
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# CHART 4: PAYER COST BY WEEK
# ----------------------------
if "PAYER_NAME" in df.columns:
    st.subheader("🏦 Weekly Claim Cost by Payer")
    payer_weekly = (
        filtered_df.groupby(["WEEK", "PAYER_NAME"])["TOTAL_CLAIM_COST"]
        .sum()
        .reset_index()
    )
    fig4 = px.line(
        payer_weekly,
        x="WEEK",
        y="TOTAL_CLAIM_COST",
        color="PAYER_NAME",
        title="Weekly Claim Cost by Payer",
        markers=True
    )
    st.plotly_chart(fig4, use_container_width=True)

# ----------------------------
# TABLE
# ----------------------------
st.markdown("### 📋 Weekly Performance Table")
st.dataframe(
    weekly_summary.tail(10)
)

