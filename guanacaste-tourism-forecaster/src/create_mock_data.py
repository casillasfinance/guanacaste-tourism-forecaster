import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def create_mock_data():
    print("Generando datos simulados para Guanacaste Tourism Forecaster...")
    
    # Rango de fechas: Enero 2018 a Diciembre 2024
    dates = pd.date_range(start="2018-01-01", end="2024-12-31", freq='ME')
    
    # Base: Ocupación media ~65%, con fuerte estacionalidad
    # Temporada alta: Dic, Ene, Feb, Mar, Abr
    # Temporada baja: May, Jun, Jul, Ago, Sep, Oct, Nov
    
    np.random.seed(42)
    records = []
    
    for dt in dates:
        month = dt.month
        year = dt.year
        
        # Ocupación base
        if month in [12, 1, 2, 3]:
            base_occ = np.random.uniform(0.75, 0.90)  # Alta
        elif month in [7, 8]:
            base_occ = np.random.uniform(0.60, 0.75)  # Media (veranillo)
        else:
            base_occ = np.random.uniform(0.40, 0.60)  # Baja / Verde
            
        # Impacto COVID (2020-2021)
        if year == 2020 and month >= 3:
            base_occ *= np.random.uniform(0.1, 0.3)
        elif year == 2021:
            base_occ *= np.random.uniform(0.4, 0.7)
            
        # Llegadas aeropuerto (Correlacionado con ocupación)
        arrivals = int(base_occ * 100000 + np.random.normal(5000, 2000))
        if arrivals < 0: arrivals = 0
            
        # Noches vendidas (Crecimiento de oferta año con año)
        total_rooms = 15000 + (year - 2018) * 500  # Crecimiento de cuartos instalados
        nights_sold = int(total_rooms * 30 * base_occ)
        
        records.append({
            'date': dt.strftime('%Y-%m-%d'),
            'occupancy_rate': round(base_occ, 4),
            'nights_sold': nights_sold,
            'intl_arrivals_lir': arrivals
        })
        
    df = pd.DataFrame(records)
    
    # Crear carpetas si no existen
    os.makedirs('../data/raw', exist_ok=True)
    os.makedirs('../data/processed', exist_ok=True)
    
    output_path = '../data/raw/tourism_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Datos guardados exitosamente en: {output_path}")

if __name__ == "__main__":
    create_mock_data()
