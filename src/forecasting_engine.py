import pandas as pd
import numpy as np
from prophet import Prophet
import warnings
import logging
import sys
import os

# SILENCE ALL THE NOISE
# 1. Standard Python warnings
warnings.filterwarnings('ignore')

# 2. CmdStanPy logs (the ones that say "Chain [1] start processing")
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

# 3. Prophet logs
logging.getLogger('prophet').setLevel(logging.ERROR)

# 4. Standard logging
logging.basicConfig(level=logging.ERROR)

class NullIO(object):
    def write(self, x): pass
    def flush(self): pass

def run_pro_montecarlo_forecast(
    df_raw, 
    recovery_months=12,
    econ_multiplier=1.0,
    n_samples=500  # Start with 500 for speed, 1000 is pro but can take 15s+
):
    """
    Executes a Professional Monte Carlo Cascade Simulation.
    Silences all output and returns stochastic paths.
    """
    # Redirect stdout to silence Prophet's internal print statements if any
    old_stdout = sys.stdout
    sys.stdout = NullIO()
    
    try:
        df = df_raw.copy()
        df['Arrivals_total'] = df['Arrivals_sjo'] + df['Arrivals_lir']
        
        # Prepare Shocks
        def make_shock(df, start, end):
            return ((df['DATE'] >= pd.to_datetime(start)) & (df['DATE'] <= pd.to_datetime(end))).astype(float)
        
        df['shock_covid'] = make_shock(df, '2020-03-01', '2021-05-31')
        df['shock_huelga_2018'] = make_shock(df, '2018-09-01', '2018-12-31')
        df['shock_inseguridad'] = make_shock(df, '2024-10-01', '2025-12-31')
        
        macro_cols = ['tasa_desempleo_usa', 'inflacion_usa_cpi', 'precio_petroleo_wti']
        for col in macro_cols:
            mu, sigma = df[col].mean(), df[col].std()
            df[f'{col}_z'] = (df[col] - mu) / sigma
        z_cols = [c + '_z' for c in macro_cols]
        df[z_cols] = df[z_cols].ffill().bfill()
        
        # --- MODEL A: ARRIVALS ---
        df_A = df[['DATE', 'Arrivals_total'] + z_cols + ['shock_covid', 'shock_huelga_2018', 'shock_inseguridad']].rename(columns={'DATE':'ds', 'Arrivals_total':'y'})
        m_A = Prophet(changepoint_prior_scale=0.1, yearly_seasonality=True, uncertainty_samples=n_samples)
        for c in z_cols + ['shock_covid', 'shock_huelga_2018', 'shock_inseguridad']:
            m_A.add_regressor(c)
        m_A.fit(df_A)
        
        future_A = m_A.make_future_dataframe(periods=24, freq='ME')
        for c in z_cols + ['shock_covid', 'shock_huelga_2018', 'shock_inseguridad']:
            mapping = df_A.set_index('ds')[c]
            future_A[c] = future_A['ds'].map(mapping)
            if c in z_cols:
                val = df_A[c].iloc[-1]
                if 'desempleo' in c: val *= econ_multiplier
                future_A[c] = future_A[c].fillna(val)
            else:
                future_A[c] = future_A[c].fillna(0.0)
                
        # Recovery Scenario Injection
        future_mask = future_A['ds'] > df_A['ds'].max()
        if recovery_months > 0:
            future_dates = future_A[future_mask]['ds']
            fade_values = np.linspace(0.8, 0, recovery_months)
            for i, date in enumerate(future_dates[:recovery_months]):
                future_A.loc[future_A['ds'] == date, 'shock_inseguridad'] = fade_values[i]

        # GET SAMPLES (STOCHASTIC)
        samples_A = m_A.predictive_samples(future_A)
        # We need the median forecast too for Stage 2 if we want to keep it simple, 
        # but for true MC we should feed samples into Stage 2. 
        # However, to avoid O(N^2) complexity, we use the median arrivals for Model B.
        forecast_A_summary = m_A.predict(future_A)
        
        # --- MODEL B: OCCUPANCY ---
        df_B = df[df.Guanacaste_Occupancy_Pct.notna()][['DATE','Guanacaste_Occupancy_Pct','Arrivals_total','shock_inseguridad']].rename(columns={'DATE':'ds','Guanacaste_Occupancy_Pct':'y'})
        arr_mu, arr_sigma = df_B['Arrivals_total'].mean(), df_B['Arrivals_total'].std()
        df_B['arr_z'] = (df_B['Arrivals_total'] - arr_mu) / arr_sigma
        
        m_B = Prophet(changepoint_prior_scale=0.08, yearly_seasonality=True, uncertainty_samples=n_samples)
        m_B.add_regressor('arr_z')
        m_B.add_regressor('shock_inseguridad')
        m_B.fit(df_B)
        
        future_B = m_B.make_future_dataframe(periods=24, freq='ME')
        arrivals_map = forecast_A_summary.set_index('ds')['yhat']
        future_B['arr_z'] = (future_B['ds'].map(arrivals_map).ffill() - arr_mu) / arr_sigma
        
        fA_shock_map = future_A.set_index('ds')['shock_inseguridad']
        future_B['shock_inseguridad'] = future_B['ds'].map(fA_shock_map).fillna(0.0)
        
        # STOCHASTIC SAMPLES FOR OCCUPANCY
        samples_B = m_B.predictive_samples(future_B)
        
        # Return summary stats for cleaner UI handling
        results = {
            'dates': future_B['ds'].tolist(),
            'actual_dates': df_B['ds'].tolist(),
            'actual_y': df_B['y'].tolist(),
            'median': np.percentile(samples_B['yhat'], 50, axis=1),
            'p05': np.percentile(samples_B['yhat'], 5, axis=1),
            'p95': np.percentile(samples_B['yhat'], 95, axis=1),
            'p25': np.percentile(samples_B['yhat'], 25, axis=1),
            'p75': np.percentile(samples_B['yhat'], 75, axis=1),
            'raw_samples': samples_B['yhat']
        }
        
    finally:
        sys.stdout = old_stdout
        
    return results
