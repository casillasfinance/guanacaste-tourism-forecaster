import pdfplumber
import pandas as pd
import os
import re

pdf_path = r"c:\Users\franc\Downloads\guanacaste-tourism-forecaster\guanacaste-tourism-forecaster\data\raw\2026-02_Llegadas_internacionales.pdf"
historical_csv = r"c:\Users\franc\Downloads\guanacaste-tourism-forecaster\guanacaste-tourism-forecaster\data\raw\arrivals_historical_sjo_lir.csv"

print("Extrayendo Llegadas 2026 del PDF ICT (Versión Final Parsed)...")

data_2026 = []

with pdfplumber.open(pdf_path) as pdf:
    # Page 13 (Index 12)
    text = pdf.pages[12].extract_text()
    
    parts = text.split("Cuadro 14")
    sjo_block = parts[0]
    lir_block = parts[1] if len(parts) > 1 else ""
    
    def parse_ict_numerical_line(line):
        # Line format: MonthName Part1 Part2 ... Part15 Part16
        # The last two parts are the 2026 value
        tokens = line.split()
        if len(tokens) >= 16: # 'Enero' + 16 parts for 8 years
            # The value for 2026 is the last two tokens joined
            val_str = tokens[-2] + tokens[-1]
            try:
                return int(val_str)
            except:
                return None
        return None

    # SJO
    for line in sjo_block.splitlines():
        if "Enero" in line or "Febrero" in line:
            val = parse_ict_numerical_line(line)
            if val:
                m_num = 1 if "Enero" in line else 2
                data_2026.append({'Year': 2026, 'Month': m_num, 'Arrivals_sjo': val})
                
    # LIR
    for line in lir_block.splitlines():
        if "Enero" in line or "Febrero" in line:
            val = parse_ict_numerical_line(line)
            if val:
                m_num = 1 if "Enero" in line else 2
                data_2026.append({'Year': 2026, 'Month': m_num, 'Arrivals_lir': val})

df_new = pd.DataFrame(data_2026)
if not df_new.empty:
    df_2026 = df_new.groupby(['Year', 'Month']).sum().reset_index()
    df_hist = pd.read_csv(historical_csv)
    df_final = pd.concat([df_hist, df_2026], ignore_index=True)
    df_final = df_final.sort_values(['Year', 'Month']).drop_duplicates(['Year', 'Month'], keep='last')
    
    os.makedirs('data/processed', exist_ok=True)
    df_final.to_csv('data/processed/arrivals_clean.csv', index=False)
    print(f"Exito: {len(df_final)} meses consolidados en data/processed/arrivals_clean.csv")
else:
    print("Error: No se pudo parsear el texto del PDF.")
