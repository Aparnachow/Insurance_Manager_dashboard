import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib
import os
from sklearn.ensemble import RandomForestRegressor

# ----------------------------------------------------
# PAGE TITLE
# ----------------------------------------------------
st.title("🔮 Predictive Insights — ML Forecasting & Risk Analytics")

st.markdown("""
This page provides:
- Random Forest–based cost prediction  
- Payer analytics  
- Diabetes & dialysis comparisons  
- Fraud & anomaly detection  
- High-risk patient identification  
- PMPM dashboard  
- Future forecasting  
""")

# ----------------------------------------------------
# LOAD FINAL MERGED DATA
# ----------------------------------------------------
data_path = "data/final_merged.csv"

if not os.path.exists(data_path):
    st.error("❌ final_merged.csv not found! Please place it in /data/")
    st.stop()

df = pd.read_csv(data_path)

# Convert date
df["ENCOUNTER_DATE"] = pd.to_datetime(df["ENCOUNTER_DATE"], errors="coerce")
df["YEAR"] = df["ENCOUNTER_DATE"].dt.year
df["MONTH"] = df["ENCOUNTER_DATE"].dt.to_period("M").astype(str)

# ----------------------------------------------------
# LOAD MODEL
# ----------------------------------------------------
model_path = "models/cost_rf_model.pkl"

st.subheader("📌 Predict Using Trained Random Forest Model")

if not os.path.exists(model_path):
    st.error("❌ Trained model not found.")
else:
    model = joblib.load(model_path)
    st.success("✅ Random Forest model loaded successfully.")

# Upload for prediction
uploaded = st.file_uploader(
    "Upload CSV matching model features (AGE, IsDiabetes, IsDialysis)",
    type=["csv"]
)

if uploaded:
    new = pd.read_csv(uploaded)
    st.write("### Preview of Uploaded File:")
    st.dataframe(new.head())

    required = list(model.feature_names_in_)
    missing = [c for c in required if c not in new.columns]

    if missing:
        st.error(f"❌ Missing columns: {missing}")
        st.stop()

    preds = model.predict(new[required])
    new["Predicted_Cost"] = preds

    st.success("🎉 Prediction Completed!")
    st.dataframe(new)

    fig_pred = px.histogram(new, x="Predicted_Cost", nbins=50,
                            title="Predicted Claim Cost Distribution")
    st.plotly_chart(fig_pred, use_container_width=True)

# ----------------------------------------------------
# ADVANCED ANALYTICS TABS
# ----------------------------------------------------
st.markdown("---")
tabs = st.tabs([
    "🏦 Payer Analytics",
    "🩺 Diabetes & Dialysis",
    "🚨 Fraud Detection",
    "⚠️ High Risk Patients",
    "💵 PMPM Dashboard",
    "📈 Forecasting"
])

# ----------------------------------------------------
# TAB 1 — PAYER ANALYTICS
# ----------------------------------------------------
with tabs[0]:
    st.header("🏦 Payer Analytics")

    if "PAYER" not in df.columns:
        st.warning("Missing PAYER column in final_merged.csv")
    else:
        payer_cost = df.groupby("PAYER")["TOTAL_CLAIM_COST"].sum().reset_index()

        fig = px.bar(payer_cost, x="PAYER", y="TOTAL_CLAIM_COST",
                     title="Total Claim Cost by Payer")
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# TAB 2 — DIABETES & DIALYSIS
# ----------------------------------------------------
with tabs[1]:
    st.header("🩺 Diabetes & Dialysis Analysis")

    col1, col2 = st.columns(2)
    col1.metric("Diabetes Patients", df[df["IsDiabetes"] == 1]["PATIENT_ID"].nunique())
    col2.metric("Dialysis Patients", df[df["IsDialysis"] == 1]["PATIENT_ID"].nunique())

    cost = pd.DataFrame({
        "Condition": ["Diabetes", "Dialysis"],
        "Cost": [
            df[df["IsDiabetes"] == 1]["TOTAL_CLAIM_COST"].sum(),
            df[df["IsDialysis"] == 1]["TOTAL_CLAIM_COST"].sum(),
        ]
    })

    fig = px.bar(cost, x="Condition", y="Cost", title="Cost Comparison")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# TAB 3 — FRAUD DETECTION
# ----------------------------------------------------
with tabs[2]:
    st.header("🚨 Fraud & Anomaly Detection")

    df["Z"] = (df["TOTAL_CLAIM_COST"] - df["TOTAL_CLAIM_COST"].mean()) / df["TOTAL_CLAIM_COST"].std()
    outliers = df[df["Z"].abs() > 3]

    fig = px.scatter(df, x="PATIENT_ID", y="TOTAL_CLAIM_COST",
                     color=df["Z"].abs() > 3,
                     title="Outlier Detection (Z > 3)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Outlier Claims")
    st.dataframe(outliers)

# ----------------------------------------------------
# TAB 4 — HIGH RISK PATIENTS
# ----------------------------------------------------
with tabs[3]:
    st.header("⚠️ High Risk Patients")

    df["RiskScore"] = (
        df["TOTAL_CLAIM_COST"].rank(pct=True)
        + df["IsDiabetes"] * 0.6
        + df["IsDialysis"] * 0.8
        + (df["AGE"] / df["AGE"].max())
    )

    top = df.sort_values("RiskScore", ascending=False).head(25)
    st.dataframe(top)

    fig = px.bar(top, x="PATIENT_ID", y="RiskScore",
                 title="Top 25 High-Risk Patients")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# TAB 5 — PMPM DASHBOARD
# ----------------------------------------------------
with tabs[4]:
    st.header("💵 PMPM Dashboard")

    members = df.groupby("MONTH")["PATIENT_ID"].nunique().reset_index()
    members.columns = ["MONTH", "Members"]

    monthly_cost = df.groupby("MONTH")["TOTAL_CLAIM_COST"].sum().reset_index()

    pmpm = monthly_cost.merge(members, on="MONTH")
    pmpm["PMPM"] = pmpm["TOTAL_CLAIM_COST"] / pmpm["Members"]

    fig = px.line(pmpm, x="MONTH", y="PMPM", title="Per Member Per Month (PMPM)")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pmpm)

# ----------------------------------------------------
# TAB 6 — FORECASTING
# ----------------------------------------------------
with tabs[5]:
    st.header("📈 12-Month Forecasting")

    monthly = df.groupby("MONTH")["TOTAL_CLAIM_COST"].sum().reset_index()
    monthly["i"] = np.arange(len(monthly))

    X = monthly[["i"]]
    y = monthly["TOTAL_CLAIM_COST"]

    rf = RandomForestRegressor(n_estimators=200)
    rf.fit(X, y)

    future_i = np.arange(len(monthly), len(monthly) + 12)
    future_pred = rf.predict(future_i.reshape(-1, 1))

    forecast = pd.DataFrame({
        "MONTH_IDX": future_i,
        "Forecasted_Cost": future_pred
    })

    st.dataframe(forecast)

    fig = px.line(forecast, x="MONTH_IDX", y="Forecasted_Cost",
                  title="12-Month Forecast")
    st.plotly_chart(fig, use_container_width=True)
