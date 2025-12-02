import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.title("🚨 Fraud & Anomaly Detection")

data_path = "data/cleaned_claims_full.csv"
if not os.path.exists(data_path):
    st.error("❌ Data file missing.")
    st.stop()

df = pd.read_csv(data_path)

# Z-score anomaly detection
st.header("1️⃣ High Claim Cost Outliers (Z-Score)")

df["Z_SCORE"] = (df["TOTAL_CLAIM_COST"] - df["TOTAL_CLAIM_COST"].mean()) / df["TOTAL_CLAIM_COST"].std()
outliers = df[df["Z_SCORE"].abs() > 3]

fig = px.scatter(df, x="PATIENT", y="TOTAL_CLAIM_COST",
                 color=df["Z_SCORE"].abs() > 3,
                 title="Cost Outliers (Z-Score > 3)")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Outlier Claims")
st.dataframe(outliers)

# Duplicate claims
st.header("2️⃣ Duplicate Claims Detection")

duplicates = df[df.duplicated(subset=["PATIENT","ENCOUNTER_DATE","TOTAL_CLAIM_COST"], keep=False)]
st.dataframe(duplicates)

# Suspicious payer behaviour
st.header("3️⃣ Suspicious Payer Behaviour")

payer_avg = df.groupby("PAYER")["TOTAL_CLAIM_COST"].mean().reset_index()
fig2 = px.bar(payer_avg, x="PAYER", y="TOTAL_CLAIM_COST",
              title="Average Claim Cost Per Payer (Unusual Spikes Detected)")
st.plotly_chart(fig2, use_container_width=True)
