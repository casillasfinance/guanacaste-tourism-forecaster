import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "id": "header",
   "metadata": {},
   "source": [
    "# 🔮 Guanacaste Tourism Forecaster — Fase 4: Cascade Forecasting\n",
    "### Proyección de Llegadas y Ocupación 2026-2027 con Prophet\n",
    "---\n",
    "**Estrategia:** Cascade de 2 etapas (Entropía controlada)\n",
    "- **Modelo A:** Proyectar llegadas aéreas (SJO + LIR) con regresores macro\n",
    "- **Modelo B:** Proyectar ocupación Guanacaste usando llegadas proyectadas como regresor\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "setup",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import warnings\n",
    "import os\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "import plotly.graph_objects as go\n",
    "import plotly.io as pio\n",
    "\n",
    "# CONFIGURACION VS CODE RENDERER\n",
    "# Si no ves los graficos, cambia 'iframe' por 'notebook' o 'vscode'\n",
    "pio.renderers.default = 'iframe'\n",
    "\n",
    "from prophet import Prophet\n",
    "\n",
    "TEMPLATE = 'plotly_dark'\n",
    "COLORS = {\n",
    "    'total':    '#f9c74f',\n",
    "    'ocupacion':'#ff6b6b',\n",
    "    'forecast': '#a855f7',\n",
    "    'ci':       'rgba(168,85,247,0.15)',\n",
    "}\n",
    "\n",
    "print('✅ Entorno listo. Directorio actual:', os.getcwd())\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "load_md",
   "metadata": {},
   "source": [
    "---\n",
    "## 1. Carga de Datos\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "load_data",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Intentar cargar datos con path relativo flexible\n",
    "data_path = '../data/merged/master_tourism_data.csv'\n",
    "if not os.path.exists(data_path):\n",
    "    data_path = 'data/merged/master_tourism_data.csv'\n",
    "    \n",
    "df = pd.read_csv(data_path)\n",
    "df['DATE'] = pd.to_datetime(df['DATE'])\n",
    "df = df.sort_values('DATE').reset_index(drop=True)\n",
    "df['Arrivals_total'] = df['Arrivals_sjo'] + df['Arrivals_lir']\n",
    "\n",
    "# Normalizacion\n",
    "macro_cols = ['tasa_desempleo_usa', 'inflacion_usa_cpi', 'precio_petroleo_wti']\n",
    "for col in macro_cols:\n",
    "    mu, sigma = df[col].mean(), df[col].std()\n",
    "    df[f'{col}_z'] = (df[col] - mu) / sigma\n",
    "z_cols = [c + '_z' for c in macro_cols]\n",
    "df[z_cols] = df[z_cols].ffill().bfill()\n",
    "\n",
    "print(f'✅ Datos cargados: {len(df)} meses. Rango: {df.DATE.min().date()} a {df.DATE.max().date()}')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "shocks",
   "metadata": {},
   "outputs": [],
   "source": [
    "def make_shock(df, start, end):\n",
    "    return ((df['DATE'] >= pd.to_datetime(start)) & (df['DATE'] <= pd.to_datetime(end))).astype(float)\n",
    "\n",
    "df['shock_covid'] = make_shock(df, '2020-03-01', '2021-05-31')\n",
    "df['shock_huelga_2018'] = make_shock(df, '2018-09-01', '2018-12-31')\n",
    "df['shock_inseguridad'] = make_shock(df, '2024-10-01', '2025-12-31')\n",
    "\n",
    "SHOCK_COLS = ['shock_covid', 'shock_huelga_2018', 'shock_inseguridad']\n",
    "print('✅ Shocks historicos definidos.')\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "modelA_md",
   "metadata": {},
   "source": [
    "---\n",
    "## 2. ETAPA 1: Llegadas Aéreas Totales\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "modelA_train",
   "metadata": {},
   "outputs": [],
   "source": [
    "print('⏳ Entrenando Modelo A (Llegadas)... esto puede tardar unos segundos...')\n",
    "df_A = df[['DATE', 'Arrivals_total'] + z_cols + SHOCK_COLS].rename(columns={'DATE':'ds', 'Arrivals_total':'y'})\n",
    "m_A = Prophet(changepoint_prior_scale=0.1, yearly_seasonality=True)\n",
    "for c in z_cols + SHOCK_COLS: m_A.add_regressor(c)\n",
    "m_A.fit(df_A)\n",
    "\n",
    "future_A = m_A.make_future_dataframe(periods=22, freq='ME')\n",
    "for c in z_cols + SHOCK_COLS:\n",
    "    mapping = df_A.set_index('ds')[c]\n",
    "    future_A[c] = future_A['ds'].map(mapping)\n",
    "    if c in z_cols: future_A[c] = future_A[c].fillna(df_A[c].iloc[-1])\n",
    "    else: future_A[c] = future_A[c].fillna(0.0)\n",
    "\n",
    "# Aplicar escenario de recuperacion 2026\n",
    "mask_2026 = (future_A['ds'] >= '2026-01-01') & (future_A['ds'] <= '2026-12-31')\n",
    "future_A.loc[mask_2026, 'shock_inseguridad'] = 0.4\n",
    "future_A.loc[future_A['ds'] >= '2027-01-01', 'shock_inseguridad'] = 0.0\n",
    "\n",
    "forecast_A = m_A.predict(future_A)\n",
    "print('✅ Modelo A completado.')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "modelA_plot",
   "metadata": {},
   "outputs": [],
   "source": [
    "fig1 = go.Figure()\n",
    "fig1.add_trace(go.Scatter(x=df_A['ds'], y=df_A['y'], name='Histórico', mode='lines', line=dict(color=COLORS['total'])))\n",
    "fig1.add_trace(go.Scatter(x=forecast_A['ds'], y=forecast_A['yhat'], name='Proyección', mode='lines', line=dict(color=COLORS['forecast'], dash='dash')))\n",
    "fig1.update_layout(title='Pronóstico de Llegadas Internacionales (SJO+LIR)', template=TEMPLATE, hovermode='x unified')\n",
    "fig1.show() # Usar .show() directo es mas compatible\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "modelB_md",
   "metadata": {},
   "source": [
    "---\n",
    "## 3. ETAPA 2: Ocupación Hotelera Guanacaste (Cascade)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "modelB_train",
   "metadata": {},
   "outputs": [],
   "source": [
    "print('⏳ Entrenando Modelo B (Ocupación) usando la cascada...')\n",
    "df_B = df[df.Guanacaste_Occupancy_Pct.notna()][['DATE','Guanacaste_Occupancy_Pct','Arrivals_total','shock_inseguridad']].rename(columns={'DATE':'ds','Guanacaste_Occupancy_Pct':'y'})\n",
    "arr_mu, arr_sigma = df_B['Arrivals_total'].mean(), df_B['Arrivals_total'].std()\n",
    "df_B['arr_z'] = (df_B['Arrivals_total'] - arr_mu) / arr_sigma\n",
    "\n",
    "m_B = Prophet(changepoint_prior_scale=0.08, yearly_seasonality=True)\n",
    "m_B.add_regressor('arr_z')\n",
    "m_B.add_regressor('shock_inseguridad')\n",
    "m_B.fit(df_B)\n",
    "\n",
    "future_B = m_B.make_future_dataframe(periods=22, freq='ME')\n",
    "arrivals_map = forecast_A.set_index('ds')['yhat']\n",
    "future_B['arr_z'] = (future_B['ds'].map(arrivals_map).ffill() - arr_mu) / arr_sigma\n",
    "shock_map = future_A.set_index('ds')['shock_inseguridad']\n",
    "future_B['shock_inseguridad'] = future_B['ds'].map(shock_map).fillna(0.0)\n",
    "\n",
    "forecast_B = m_B.predict(future_B)\n",
    "forecast_B['yhat'] = forecast_B['yhat'].clip(0, 100)\n",
    "print('✅ Modelo B completado.')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "modelB_plot",
   "metadata": {},
   "outputs": [],
   "source": [
    "fig2 = go.Figure()\n",
    "fig2.add_trace(go.Scatter(x=df_B['ds'], y=df_B['y'], name='Real', mode='lines+markers', line=dict(color=COLORS['ocupacion'])))\n",
    "fig2.add_trace(go.Scatter(x=forecast_B['ds'], y=forecast_B['yhat'], name='Proyectado', mode='lines', line=dict(color=COLORS['forecast'])))\n",
    "fig2.update_layout(title='Pronóstico de Ocupación Hotelera Guanacaste (%)', template=TEMPLATE, yaxis=dict(range=[0,105]))\n",
    "fig2.show()\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "results_md",
   "metadata": {},
   "source": [
    "---\n",
    "## 4. Tabla de Resultados (Proyección 2026)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "results",
   "metadata": {},
   "outputs": [],
   "source": [
    "res = forecast_B[forecast_B['ds'] > '2025-12-31'][['ds','yhat']].head(12)\n",
    "res.columns = ['Mes','Ocupacion_Pct']\n",
    "res['Mes'] = res['Mes'].dt.strftime('%B %Y')\n",
    "print(res.to_string(index=False))\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.11.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

with open('notebooks/04_modeling_prophet.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("Notebook 04_modeling_prophet.ipynb REPARADO con paths flexibles y renderers estables.")
