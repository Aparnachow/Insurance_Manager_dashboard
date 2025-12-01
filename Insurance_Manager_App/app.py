import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Insurance Manager Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ----------------------------------------------------
# PAGE TITLE
# ----------------------------------------------------
st.title("🏥 Insurance Manager Dashboard")
st.markdown("Monitor insurance claims, costs, risks, and forecasting for chronic conditions like **Dialysis** and **Diabetes**.")

st.markdown("---")
st.subheader("📚 Navigation Guide")

st.markdown("""
Welcome to the Insurance Manager dashboard.  
Use the sidebar to navigate through the different analytics pages.
""")

# ----------------------------------------------------
# ⭐ PROJECT PURPOSE (NEW SECTION)
# ----------------------------------------------------
st.markdown("""
### 🎯 **Project Purpose**

This dashboard was developed for the **Insurance Manager** to streamline healthcare claim analysis and improve decision-making.  
It integrates **clinical, financial, and operational datasets** generated using Synthea’s synthetic EHR data, and applies both **statistical** and **machine-learning methods** to support:

- Monitoring claim volumes, high-cost cases, and anomalies  
- Evaluating payer performance and acceptance behavior  
- Studying trends for chronic conditions like diabetes and dialysis  
- Identifying high-risk patients through ML-based risk scoring  
- Tracking **Per Member Per Month (PMPM)** cost trends  
- Forecasting future claim costs using trained ML models  

Together, these insights enable proactive cost control and more informed insurance management.
""")

st.markdown("---")

# ----------------------------------------------------
# AVAILABLE PAGES
# ----------------------------------------------------
st.subheader("📂 Available Pages")

st.markdown("""
### **Core Analytics Pages**
- **Daily View:** Operational alerts (pending vs processed claims, frauds)  
- **Weekly Performance:** Efficiency by provider and payer  
- **Monthly Overview:** PMPM trends, denial rate, cost share  
- **Predictive Insights:** Claim cost forecasting using Random Forest  
- **Payer Analytics:** Total cost, acceptance rate, average cost, payer trends  

### **Advanced Analytics Pages (5–10)**
- **Dialysis Diabetes Analysis:** Chronic condition cost, risk, age groups, city trends  
- **Fraud Anomaly Detection:** Outliers, duplicates, suspicious payer behavior  
- **High Risk Patients:** Patient risk scores, age–risk analysis  
- **PMPM Dashboard:** Per Member Per Month cost and member trends  
- **Forecasting Dashboard:** Real month-based future claim cost prediction  
""")

st.markdown("---")

st.info("Choose a page from the left sidebar to begin analyzing your Synthea dataset.")
st.warning("This homepage only provides navigation. All analytics appear in the pages under the **pages/** folder.")
