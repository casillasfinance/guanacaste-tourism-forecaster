import pandas as pd
import numpy as np
from prophet import Prophet
import os
import warnings

warnings.filterwarnings('ignore')

# 1. Load Data
df = pd.read_csv('data/merged/master_tourism_data.csv')
df['DATE'] = pd.to_datetime(df['DATE'])
df['Arrivals_total'] = df['Arrivals_sjo'] + df['Arrivals_lir']

# 2. Shocks
def make_shock(df, start, end):
    s, e = pd.to_datetime(start), pd.to_datetime(end)
    return ((df['DATE'] >= s) & (df['DATE'] <= e)).astype(float)

df['shock_covid'] = make_shock(df, '2020-03-01', '2021-05-31')
df['shock_huelga_2018'] = make_shock(df, '2018-09-01', '2018-12-31')
df['shock_inseguridad'] = make_shock(df, '2024-10-01', '2025-12-31')

macro_cols = ['tasa_desempleo_usa', 'inflacion_usa_cpi', 'precio_petroleo_wti']
# Normalize
for col in macro_cols:
    mu, sigma = df[col].mean(), df[col].std()
    df[f'{col}_z'] = (df[col] - mu) / sigma
z_cols = [f'{col}_z' for col in macro_cols]
df[z_cols] = df[z_cols].ffill().bfill()

# 3. Model A: Arrivals
df_A = df[['DATE', 'Arrivals_total'] + z_cols + ['shock_covid','shock_huelga_2018','shock_inseguridad']].copy()
df_A = df_A.rename(columns={'DATE': 'ds', 'Arrivals_total': 'y'})

m_A = Prophet(changepoint_prior_scale=0.1, seasonality_prior_scale=10.0, yearly_seasonality=True)
for c in z_cols + ['shock_covid','shock_huelga_2018','shock_inseguridad']:
    m_A.add_regressor(c)

m_A.fit(df_A)

future_A = m_A.make_future_dataframe(periods=22, freq='ME') # to Dec 2027

# Map historical values to future_A to avoid NaNs
for c in z_cols + ['shock_covid','shock_huelga_2018','shock_inseguridad']:
    mapping = df_A.set_index('ds')[c]
    future_A[c] = future_A['ds'].map(mapping)

# Fill future dates
last_vals = df_A[z_cols].iloc[-1]
for c in z_cols:
    future_A[c] = future_A[c].fillna(last_vals[c])

future_A['shock_covid'] = future_A['shock_covid'].fillna(0.0)
future_A['shock_huelga_2018'] = future_A['shock_huelga_2018'].fillna(0.0)

# Scenario for insecurity shock in the future
mask_2026 = (future_A['ds'] >= '2026-01-01') & (future_A['ds'] <= '2026-12-31')
future_A.loc[mask_2026, 'shock_inseguridad'] = 0.4
future_A.loc[future_A['ds'] >= '2027-01-01', 'shock_inseguridad'] = 0.0
future_A['shock_inseguridad'] = future_A['shock_inseguridad'].fillna(0.0)

forecast_A = m_A.predict(future_A)

# 4. Model B: Occupancy (Cascade)
df_B = df[df.Guanacaste_Occupancy_Pct.notna()].copy()
df_B = df_B.rename(columns={'DATE':'ds', 'Guanacaste_Occupancy_Pct':'y'})
# Normalize Arrivals to use as regressor
arr_mu, arr_sigma = df_B['Arrivals_total'].mean(), df_B['Arrivals_total'].std()
df_B['arr_z'] = (df_B['Arrivals_total'] - arr_mu) / arr_sigma

m_B = Prophet(changepoint_prior_scale=0.08, yearly_seasonality=True)
m_B.add_regressor('arr_z')
m_B.add_regressor('shock_inseguridad')
m_B.fit(df_B)

future_B = m_B.make_future_dataframe(periods=22, freq='ME')
# Use results from A as regressor for B
arrivals_map = forecast_A.set_index('ds')['yhat']
future_B['arr_z'] = (future_B['ds'].map(arrivals_map).ffill() - arr_mu) / arr_sigma

# Map shock_inseguridad from future_A
shock_map = future_A.set_index('ds')['shock_inseguridad']
future_B['shock_inseguridad'] = future_B['ds'].map(shock_map).fillna(0.0)

forecast_B = m_B.predict(future_B)

# 5. Export
os.makedirs('reports', exist_ok=True)
res = forecast_B[['ds', 'yhat']].copy()
res = res[res['ds'] > '2025-12-25'] # Only future for the summary
res.columns = ['Fecha', 'Ocupacion_Proyectada_%']
res['Fecha'] = res['Fecha'].dt.strftime('%b %Y')
res['Ocupacion_Proyectada_%'] = res['Ocupacion_Proyectada_%'].round(1).clip(0, 100)
res.to_csv('reports/final_forecast_2027.csv', index=False)

print("--- RESULTADOS MODELO CASCADE (Proyeccion 2026-2027) ---")
print(res.to_string(index=False))
