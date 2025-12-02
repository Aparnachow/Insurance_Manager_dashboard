import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

# ----------------------------
# PAGE TITLE
# ----------------------------
st.title("💰 Monthly Financial Overview")

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

# Extract month
df["MONTH"] = df["DATE"].dt.to_period("M").astype(str)

# ----------------------------
# MONTHLY SUMMARY
# ----------------------------
monthly = df.groupby("MONTH").agg({
    "TOTAL_CLAIM_COST": "sum",
    "IsDiabetes": "sum",
    "IsDialysis": "sum"
}).reset_index()

# Calculate PMPM (Per Member Per Month)
if "PATIENT" in df.columns:
    member_months = df.groupby("MONTH")["PATIENT"].nunique().reset_index(name="UNIQUE_PATIENTS")
    monthly = monthly.merge(member_months, on="MONTH", how="left")
    monthly["PMPM"] = monthly["TOTAL_CLAIM_COST"] / monthly["UNIQUE_PATIENTS"]

# ----------------------------
# KPIs
# ----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("💵 Total Cost", f"${df['TOTAL_CLAIM_COST'].sum():,.0f}")
col2.metric("📆 Months in Data", f"{monthly.shape[0]}")
col3.metric("👥 Avg PMPM", f"${monthly['PMPM'].mean():,.0f}" if "PMPM" in monthly.columns else "N/A")

st.markdown("---")

# ----------------------------
# CHART 1: MONTHLY CLAIM COST
# ----------------------------
st.subheader("📈 Monthly Total Claim Cost Trend")
fig1 = px.line(
    monthly,
    x="MONTH",
    y="TOTAL_CLAIM_COST",
    title="Total Claim Cost by Month",
    markers=True,
    color_discrete_sequence=["#1565C0"]
)
st.plotly_chart(fig1, use_container_width=True)

# ----------------------------
# CHART 2: DISEASE SHARE
# ----------------------------
st.subheader("🏥 Diabetes vs Dialysis — Monthly Trends")
fig2 = px.bar(
    monthly,
    x="MONTH",
    y=["IsDiabetes", "IsDialysis"],
    barmode="group",
    title="Chronic Condition Counts per Month"
)
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# CHART 3: PMPM TREND
# ----------------------------
if "PMPM" in monthly.columns:
    st.subheader("📊 PMPM Trend (Per Member Per Month)")
    fig3 = px.line(
        monthly,
        x="MONTH",
        y="PMPM",
        title="PMPM Trend by Month",
        markers=True,
        color_discrete_sequence=["#2E8B57"]
    )
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# TABLE
# ----------------------------
st.markdown("### 📋 Monthly Summary Table")
st.dataframe(monthly.tail(10))

# ----------------------------
# 🔮 PAYER-LEVEL FORECASTS (2025–2030)
# ----------------------------
st.markdown("---")
st.subheader("🏦 Forecast by Payer (2025–2030)")

if "PAYER" in df.columns:
    payers = df["PAYER"].dropna().unique().tolist()
    selected_payer = st.selectbox("Select a Payer to Forecast:", payers)

    # Filter data for that payer
    payer_df = df[df["PAYER"] == selected_payer].copy()
    payer_df["MONTH"] = pd.to_datetime(payer_df["DATE"], errors="coerce").dt.to_period("M").astype(str)
    payer_monthly = payer_df.groupby("MONTH")["TOTAL_CLAIM_COST"].sum().reset_index()

    if payer_monthly.shape[0] >= 6:
        # Prepare data for Prophet
        payer_forecast_data = payer_monthly.rename(columns={"MONTH": "ds", "TOTAL_CLAIM_COST": "y"})
        payer_forecast_data["ds"] = pd.to_datetime(payer_forecast_data["ds"])

        # Train the model
        payer_model = Prophet(yearly_seasonality=True, daily_seasonality=False)
        payer_model.fit(payer_forecast_data)

        # Create future dates
        future_payer = payer_model.make_future_dataframe(periods=60, freq="M")

        # Predict
        payer_forecast = payer_model.predict(future_payer)

        # Plot forecast
        fig_payer = px.line(
            payer_forecast,
            x="ds",
            y="yhat",
            title=f"Projected Claim Cost for {selected_payer} (2025–2030)",
            color_discrete_sequence=["#1565C0"]
        )
        st.plotly_chart(fig_payer, use_container_width=True)

        # Show last few predictions
        st.markdown(f"### 📋 Forecast Summary for {selected_payer}")
        st.dataframe(payer_forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(12))
    else:
        st.warning(f"⚠️ Not enough data to forecast for {selected_payer} (needs ≥ 6 months of data).")
else:
    st.warning("⚠️ No 'PAYER' column found in your dataset. Please include payer information in cleaned_claims_full.csv.")
