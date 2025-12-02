import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import os

st.title("🔮 Forecasting — Future Claim Cost Prediction")

# ---------------------------
# LOAD DATA
# ---------------------------
data_path = "data/cleaned_claims_full.csv"
if not os.path.exists(data_path):
    st.error("❌ Data file missing.")
    st.stop()

df = pd.read_csv(data_path)
df["ENCOUNTER_DATE"] = pd.to_datetime(df["ENCOUNTER_DATE"], errors="coerce")

# ---------------------------
# CREATE YEAR-MONTH COLUMN
# ---------------------------
df["YEAR_MONTH"] = df["ENCOUNTER_DATE"].dt.to_period("M").astype(str)

# Monthly totals
monthly_costs = df.groupby("YEAR_MONTH")["TOTAL_CLAIM_COST"].sum().reset_index()

# SORT by date
monthly_costs["YEAR_MONTH"] = pd.to_datetime(monthly_costs["YEAR_MONTH"])
monthly_costs = monthly_costs.sort_values("YEAR_MONTH").reset_index(drop=True)

# ---------------------------
# ADD DATE INDEX FOR MODEL
# ---------------------------
monthly_costs["MONTH_IDX"] = np.arange(len(monthly_costs))

# Prepare model data
X = monthly_costs[["MONTH_IDX"]]
y = monthly_costs["TOTAL_CLAIM_COST"]

rf = RandomForestRegressor(n_estimators=200)
rf.fit(X, y)

# ---------------------------
# FORECAST NEXT 12 MONTHS
# ---------------------------
last_date = monthly_costs["YEAR_MONTH"].max()

future_dates = pd.date_range(
    start=last_date + pd.DateOffset(months=1),
    periods=12,
    freq="MS"
)

future_idx = np.arange(len(monthly_costs), len(monthly_costs) + 12)
future_pred = rf.predict(future_idx.reshape(-1, 1))

forecast_df = pd.DataFrame({
    "YEAR_MONTH": future_dates,
    "Forecasted_Cost": future_pred
})

# REAL DATE LABEL = "2024-05 (May 2024)"
forecast_df["LABEL"] = forecast_df["YEAR_MONTH"].dt.strftime("%Y-%m (%b %Y)")

# ---------------------------
# DISPLAY CHART
# ---------------------------
st.header("📈 Forecasted Claim Cost for Next 12 Months")

fig = px.line(
    forecast_df,
    x="LABEL",
    y="Forecasted_Cost",
    markers=True,
    title="Future Claim Cost Forecast (Next 12 Months)",
    labels={"LABEL": "Month", "Forecasted_Cost": "Forecasted Claim Cost"}
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# SHOW FORECAST TABLE
# ---------------------------
st.header("📄 Forecast Table")
st.dataframe(forecast_df)
