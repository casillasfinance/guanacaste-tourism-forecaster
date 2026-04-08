import pandas as pd
import numpy as np
import datetime
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_fred_macro_data(start_date: str = '2009-01-01') -> pd.DataFrame:
    """
    Descarga directamente desde la API de FRED (Reserva Federal) los datos macroeconómicos 
    clave y los agrupa de forma mensual.
    """
    logger.info(f"Iniciando descarga de datos macro desde FRED a partir de {start_date}...")
    
    series = {
        'UNRATE': 'tasa_desempleo_usa',                 
        'USINFO': 'empleo_sector_tech_usa',             
        'UMCSENT': 'sentimiento_consumidor_michi',      
        'CPIAUCSL': 'inflacion_usa_cpi',                
        'DCOILWTICO': 'precio_petroleo_wti',            
        'DSPIC96': 'ingreso_disponible_usa'             
    }
    
    df_list = []
    
    for s_id, s_name in series.items():
        try:
            url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={s_id}'
            df_temp = pd.read_csv(url, parse_dates=['observation_date'], na_values='.')
            df_temp = df_temp.rename(columns={'observation_date': 'DATE'})
            
            df_temp = df_temp[df_temp['DATE'] >= start_date].copy()
            df_temp[s_id] = pd.to_numeric(df_temp[s_id], errors='coerce')
            
            df_temp.set_index('DATE', inplace=True)
            df_temp = df_temp.resample('ME').mean()  
            df_temp.rename(columns={s_id: s_name}, inplace=True)
            
            df_list.append(df_temp)
        except Exception as e:
            logger.error(f"Error descargando la serie {s_id}: {e}")
            
    df_macro = pd.concat(df_list, axis=1)
    df_macro.reset_index(inplace=True)
    df_macro['DATE'] = df_macro['DATE'].dt.strftime('%Y-%m-%d')
    logger.info(f"Descarga completa de FRED exitosa. {df_macro.shape[0]} meses procesados.")
    
    return df_macro

def add_event_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inyecta todas las variables Dummy (0/1) representando los Shocks del 
    Análisis Exhaustivo 2009-2026 en el mercado turístico de Guanacaste.
    """
    logger.info("Inyectando matriz de eventos Macro y Micro (2009-2026)...")
    
    # A. MACRO-EVENTOS GLOBALES
    df['brote_h1n1_2009'] = df['DATE'].apply(lambda x: 1 if '2009-04-01' <= x <= '2009-12-31' else 0)
    df['covid_agudo_cr_mundial'] = df['DATE'].apply(lambda x: 1 if '2020-03-01' <= x <= '2021-12-31' else 0)
    df['guerra_ucrania_activa'] = df['DATE'].apply(lambda x: 1 if x >= '2022-02-01' else 0)
    df['crisis_precios_energia_global'] = df['DATE'].apply(lambda x: 1 if '2021-01-01' <= x <= '2023-12-31' else 0)
    df['stress_economico_canada'] = df['DATE'].apply(lambda x: 1 if x >= '2022-06-01' else 0)
    
    def usa_elections(fecha):
        if ('2012-11' <= fecha <= '2013-01' or 
            '2016-11' <= fecha <= '2017-01' or 
            '2020-11' <= fecha <= '2021-01' or 
            '2024-11' <= fecha <= '2025-01'):
            return 1
        return 0
    df['usa_election_season'] = df['DATE'].apply(usa_elections)
    
    # B. SHOCKS CLIMÁTICOS/REGIONALES (USA)
    def incendios_california(fecha):
        if (('2018-08' <= fecha <= '2018-11') or ('2020-08' <= fecha <= '2020-11') or 
            ('2021-08' <= fecha <= '2021-11') or ('2024-08' <= fecha <= '2024-11')):
            return 1
        return 0
    df['shock_california_fires'] = df['DATE'].apply(incendios_california)
    df['shock_florida_redtide'] = df['DATE'].apply(lambda x: 1 if '2018-07-01' <= x <= '2018-12-31' else 0)
    df['shock_florida_hurricanes'] = df['DATE'].apply(lambda x: 1 if ('2022-09' <= x <= '2022-11') or ('2024-10' <= x <= '2024-12') else 0)
    
    # C. MICRO-EVENTOS COSTA RICA / REGIONALES
    df['huelga_nacional_cr_2018'] = df['DATE'].apply(lambda x: 1 if '2018-09-01' <= x <= '2018-11-30' else 0)
    df['colapso_pista_lir_2024'] = df['DATE'].apply(lambda x: 1 if x == '2024-11-30' or x == '2024-11-01' else 0)
    df['brote_zika_latam'] = df['DATE'].apply(lambda x: 1 if '2016-02-01' <= x <= '2016-11-30' else 0)
    df['crisis_seguridad_2017_2018'] = df['DATE'].apply(lambda x: 1 if '2017-01-01' <= x <= '2018-12-31' else 0)
    df['crisis_narcotrafico_2023_2026'] = df['DATE'].apply(lambda x: 1 if x >= '2023-01-01' else 0)
    
    logger.info("Total de 14 variables exógenas añadidas con éxito.")
    return df

def run_data_preparation_pipeline():
    """Ejecuta el pipeline completo de preparación de datos macro."""
    logger.info("=== INICIANDO PIPELINE DE PREPARACIÓN DE DATOS (CRISP-DM FASE 3) ===")
    df_macro = download_fred_macro_data(start_date='2009-01-01')
    df_macro = add_event_dummies(df_macro)
    
    # Asegurar que el directorio procesado existe
    os.makedirs('data/processed', exist_ok=True)
    
    output_path = 'data/processed/macro_events_features.csv'
    df_macro.to_csv(output_path, index=False)
    logger.info(f"=== PIPELINE COMPLETADO. Datos guardados en {output_path} ===")
    
    return df_macro

if __name__ == "__main__":
    run_data_preparation_pipeline()
