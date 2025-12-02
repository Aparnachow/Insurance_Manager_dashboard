import pandas as pd
import os

# -----------------------------
# FILE PATHS
# -----------------------------
DATA_PATH = "../data/"
OUTPUT_PATH = "../data/cleaned_claims_full.csv"

# -----------------------------
# LOAD DATA
# -----------------------------
print("🧩 Loading data files...")

patients = pd.read_csv(os.path.join(DATA_PATH, "patients.csv"))
encounters = pd.read_csv(os.path.join(DATA_PATH, "encounters.csv"))
conditions = pd.read_csv(os.path.join(DATA_PATH, "conditions.csv"))
procedures = pd.read_csv(os.path.join(DATA_PATH, "procedures.csv"))
payers = pd.read_csv(os.path.join(DATA_PATH, "payers.csv"))
payer_transitions = pd.read_csv(os.path.join(DATA_PATH, "payer_transitions.csv"))

print("✅ Data loaded successfully.")

# -----------------------------
# CLEAN PATIENTS
# -----------------------------
patients = patients[['Id', 'BIRTHDATE', 'GENDER', 'CITY', 'STATE']].drop_duplicates()
patients['AGE'] = (pd.Timestamp.now().year - pd.to_datetime(patients['BIRTHDATE']).dt.year)

# -----------------------------
# CLEAN ENCOUNTERS
# -----------------------------
encounters = encounters[['PATIENT', 'START', 'TOTAL_CLAIM_COST', 'PAYER_COVERAGE', 'DESCRIPTION', 'ORGANIZATION', 'PAYER']].dropna(subset=['PATIENT'])
encounters.rename(columns={'START': 'ENCOUNTER_DATE'}, inplace=True)

# -----------------------------
# CLEAN CONDITIONS
# -----------------------------
conditions = conditions[['PATIENT', 'DESCRIPTION']].drop_duplicates()
conditions['IsDiabetes'] = conditions['DESCRIPTION'].str.contains("diabetes", case=False, na=False).astype(int)
conditions['IsDialysis'] = conditions['DESCRIPTION'].str.contains("dialysis|renal", case=False, na=False).astype(int)
conditions = conditions.groupby('PATIENT')[['IsDiabetes', 'IsDialysis']].max().reset_index()

# -----------------------------
# CLEAN PROCEDURES
# -----------------------------
procedures = procedures[['PATIENT', 'DESCRIPTION']].drop_duplicates()
procedures['IsDialysisProc'] = procedures['DESCRIPTION'].str.contains("dialysis", case=False, na=False).astype(int)
procedures = procedures.groupby('PATIENT')['IsDialysisProc'].max().reset_index()

# -----------------------------
# CLEAN PAYER TRANSITIONS
# -----------------------------
payer_transitions = payer_transitions[['PATIENT', 'PAYER', 'START_DATE', 'END_DATE']].dropna()

# -----------------------------
# MERGE ALL TABLES
# -----------------------------
print("🔄 Merging all datasets...")

# -----------------------------
# MERGE ALL TABLES
# -----------------------------
print("🧩 Merging all datasets...")

# Start with encounters (base)
df = (
    encounters
    .merge(patients, left_on='PATIENT', right_on='Id', how='left')
    .merge(conditions, on='PATIENT', how='left')
    .merge(procedures, on='PATIENT', how='left')
)

# Step 1: Ensure 'PAYER' exists in df
if "PAYER" not in df.columns and "PAYER" in encounters.columns:
    print("✅ Adding PAYER column from encounters...")
    df["PAYER"] = encounters["PAYER"]

# Step 2: Merge payer_transitions for any missing payer info
if "PAYER" in payer_transitions.columns:
    df = df.merge(payer_transitions[["PATIENT", "PAYER"]], on="PATIENT", how="left", suffixes=("", "_TRANS"))
    df["PAYER"] = df["PAYER"].fillna(df["PAYER_TRANS"])
    df.drop(columns=["PAYER_TRANS"], errors="ignore", inplace=True)

# Step 3: Merge payer names from payers.csv
print("🔍 Merging payer names...")
if "Id" in payers.columns and "NAME" in payers.columns and "PAYER" in df.columns:
    df = df.merge(payers[["Id", "NAME"]], left_on="PAYER", right_on="Id", how="left")
    df.rename(columns={"NAME": "PAYER_NAME"}, inplace=True)
    df.drop(columns=["Id"], errors="ignore", inplace=True)
    print("✅ Payer names merged successfully.")
else:
    print("⚠️ Skipping payer name merge — missing columns.")
    df["PAYER_NAME"] = "Unknown"

# Clean up duplicated or unused columns
df.drop(columns=["Id_y"], errors="ignore", inplace=True)
df.rename(columns={"Id_x": "PATIENT_ID"}, inplace=True)

# -----------------------------
# CLEANUP
# -----------------------------
df = df.drop_duplicates()
df = df.fillna({
    'IsDiabetes': 0,
    'IsDialysis': 0,
    'IsDialysisProc': 0,
    'TOTAL_CLAIM_COST': 0,
    'PAYER_COVERAGE': 0,
})

print(f"✅ Final dataset shape: {df.shape}")

# -----------------------------
# SAVE CLEAN DATA
# -----------------------------
df.to_csv(OUTPUT_PATH, index=False)
print(f"💾 Cleaned data saved to {OUTPUT_PATH}")
