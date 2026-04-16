# Guanacaste Tourism Forecaster

A professional tourism forecasting engine designed to project hotel occupancy and international arrivals for Guanacaste, Costa Rica. This project utilizes Bayesian forecasting (Prophet) and Monte Carlo simulations to evaluate economic risks and historical shocks.

## Project Overview

This repository provides a complete pipeline for tourism data analysis, from ingestion and ETL to advanced stochastic simulation. It is designed for executive-level reporting within Jupyter Notebooks, featuring interactive Plotly visualizations.

### Key Features:
- **Cascade Forecasting Model**: A 2-stage model that first projects total arrivals based on US macroeconomic indicators and then uses those projections to estimate regional hotel occupancy.
- **Monte Carlo Risk Analysis**: Stochastic simulation of 500+ potential futures to identify Value-at-Risk (VaR) and establish confidence bounds (P05/P95).
- **Macro-Economic Integration**: Automatic integration of US Unemployment Rate, CPI, and WTI Oil prices as external regressors.
- **Shock Modeling**: Historical analysis and future simulation of structural shocks like COVID-19, social unrest, and security crises.

## Directory Structure

- `data/`: Raw and processed tourist arrivals and occupancy data.
- `notebooks/`: Executive reports and modeling workflows.
  - `03_data_preparation.ipynb`: ETL and data consolidation.
  - `04_modeling_prophet.ipynb`: Baseline cascade forecasting.
  - `05_scenario_simulation.ipynb`: Monte Carlo simulation and risk maps.
- `src/`: Core Python forecasting engine.
- `reports/`: Cleaned final CSV outputs for executive summaries.
- `tests/`: Basic validation and unit tests.

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/casillasfinance/guanacaste-tourism-forecaster.git
   cd guanacaste-tourism-forecaster
   ```

2. **Set up the environment**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Open Jupyter Lab or VS Code Notebooks.
2. Run the notebooks in sequence (03 -> 04 -> 05).
3. Review the interactive Fan Charts in `05_scenario_simulation.ipynb` for the final risk-aware projection.

## Methodology

The forecasting engine uses **Facebook Prophet** for its ability to handle seasonality and non-linear trends with external regressors. The Monte Carlo layer adds a stochastic dimension to account for the uncertainty inherent in the tourism market, particularly after global shocks.

---
*Developed for professional tourism market analysis in Costa Rica.*
