import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE TITLE
# ----------------------------
st.title("📅 Daily Operational Overview")

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

# Extract date components
df["DAY"] = df["DATE"].dt.date
df["MONTH"] = df["DATE"].dt.to_period("M").astype(str)

# ----------------------------
# FILTERS
# ----------------------------
st.sidebar.header("🔍 Filters")
selected_month = st.sidebar.selectbox("Select Month:", sorted(df["MONTH"].unique()))
filtered_df = df[df["MONTH"] == selected_month]

# ----------------------------
# KPIs
# ----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("📋 Total Claims", f"{len(filtered_df):,}")
col2.metric("💰 Total Cost", f"${filtered_df['TOTAL_CLAIM_COST'].sum():,.0f}")
col3.metric("🏥 Unique Patients", f"{filtered_df['PATIENT'].nunique():,}")

st.markdown("---")

# ----------------------------
# CHART 1: DAILY CLAIMS TREND
# ----------------------------
st.subheader(f"📈 Daily Claims Trend — {selected_month}")
daily_trend = filtered_df.groupby("DAY")["TOTAL_CLAIM_COST"].sum().reset_index()
fig1 = px.line(
    daily_trend,
    x="DAY",
    y="TOTAL_CLAIM_COST",
    title="Daily Total Claim Cost",
    markers=True,
    color_discrete_sequence=["#1565C0"]
)
st.plotly_chart(fig1, use_container_width=True)

# ----------------------------
# CHART 2: TOP CONDITIONS
# ----------------------------
st.subheader("🩺 Top Chronic Conditions (Diabetes & Dialysis)")
cond_sum = {
    "Diabetes Cases": filtered_df["IsDiabetes"].sum(),
    "Dialysis Cases": filtered_df["IsDialysis"].sum()
}
cond_df = pd.DataFrame(list(cond_sum.items()), columns=["Condition", "Count"])
fig2 = px.bar(
    cond_df,
    x="Condition",
    y="Count",
    title="Daily Condition Counts",
    color="Condition",
    color_discrete_sequence=["#42A5F5", "#66BB6A"]
)
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# CHART 3: PAYER COVERAGE
# ----------------------------
if "PAYER_NAME" in df.columns:
    st.subheader("🏦 Payer Coverage Breakdown")
    payer_cost = filtered_df.groupby("PAYER_NAME")["TOTAL_CLAIM_COST"].sum().reset_index()
    fig3 = px.pie(
        payer_cost,
        names="PAYER_NAME",
        values="TOTAL_CLAIM_COST",
        title="Total Claim Cost by Payer"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# TABLE
# ----------------------------
st.markdown("### 📋 Daily Claims Table")
st.dataframe(filtered_df[["DAY", "PATIENT", "TOTAL_CLAIM_COST", "PAYER_NAME", "CITY", "STATE"]].head(20))

