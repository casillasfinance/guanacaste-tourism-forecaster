import pandas as pd
import os

# Paths
arrivals_path = 'data/processed/arrivals_clean.csv'
occupancy_path = 'data/processed/occupancy_clean.csv'

print("Iniciando Fusión Maestra de Datos...")

# 1. Load Arrivals (SJO & LIR)
df_arr = pd.read_csv(arrivals_path)
# Ensure DATE format for merging later (using 1st of month)
df_arr['DATE'] = pd.to_datetime(df_arr[['Year', 'Month']].assign(day=1))

# 2. Load Occupancy
df_occ = pd.read_csv(occupancy_path)
df_occ['DATE'] = pd.to_datetime(df_occ[['Year', 'Month']].assign(day=1))

# 3. Merge Arrivals and Occupancy
df_merged = pd.merge(df_arr, df_occ[['DATE', 'Guanacaste_Occupancy_Pct']], on='DATE', how='left')

# 4. Integrate Macro Data & Events
# We'll need to run the macro downloader logic or load from df_macro if we had it saved.
# Since we are in a script, let's just do the merge of what we have first.
# Note: The macro data was being handled in the notebook.

# For now, let's create the 'merged' directory and save the core tourism data
os.makedirs('data/merged', exist_ok=True)
df_merged.to_csv('data/merged/tourism_core_merged.csv', index=False)

print(f"Fusión parcial completada: {len(df_merged)} meses consolidados.")
print("Archivo guardado en: data/merged/tourism_core_merged.csv")

# Quick Correlation for the user
if 'Guanacaste_Occupancy_Pct' in df_merged.columns:
    corr_matrix = df_merged[['Arrivals_sjo', 'Arrivals_lir', 'Guanacaste_Occupancy_Pct']].corr()
    print("\n--- MATRIZ DE CORRELACIÓN ---")
    print(corr_matrix)
