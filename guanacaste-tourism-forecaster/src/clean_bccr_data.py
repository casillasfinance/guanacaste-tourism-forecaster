import pdfplumber
import pandas as pd
import os

pdf_path = r"c:\Users\franc\Downloads\guanacaste-tourism-forecaster\guanacaste-tourism-forecaster\data\raw\Indicadores_BCCR_2018-2024 (Ocupacion hotelera).pdf"

def clean_val(v):
    if v is None: return None
    v = str(v).replace(',', '.')
    try:
        return float(v)
    except:
        return None

print("Extrayendo Ocupación del PDF BCCR (Versión Robusta)...")

raw_data = []

with pdfplumber.open(pdf_path) as pdf:
    # Page 5 has the Cuadro 3
    page = pdf.pages[4]
    tables = page.extract_tables()
    
    # Based on inspection, we have 12 rows with numerical values
    # Each row should have 7 columns (2018, 2019, 2020, 2021, 2022, 2023, 2024)
    # But some cells are combined '80,3 83,5'
    
    if tables:
        table = tables[0]
        # Filter rows that look like data (have numbers)
        data_rows = []
        for row in table:
            # Join row to see if it has many numbers
            row_str = " ".join(str(v) for v in row if v)
            if any(char.isdigit() for char in row_str):
                data_rows.append(row)
        
        # We expect 12 rows (Jan to Dec)
        if len(data_rows) >= 12:
            # Map 12 rows to months
            for mon_idx in range(12):
                row = data_rows[mon_idx]
                # Flatten the row: split any internal spaces in cells
                flat_row = []
                for cell in row:
                    if cell:
                        # Split by space and add to flat_row
                        parts = str(cell).split()
                        flat_row.extend(parts)
                
                # Now we expect 7 columns
                years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
                for i, year in enumerate(years):
                    if i < len(flat_row):
                        val = clean_val(flat_row[i])
                        if val is not None:
                            raw_data.append({'Year': year, 'Month': mon_idx + 1, 'Guanacaste_Occupancy_Pct': val})

df_ocu = pd.DataFrame(raw_data)
if not df_ocu.empty:
    df_ocu = df_ocu.sort_values(['Year', 'Month'])
    os.makedirs('data/processed', exist_ok=True)
    df_ocu.to_csv('data/processed/occupancy_clean.csv', index=False)
    print(f"Extracción exitosa: {len(df_ocu)} registros guardados.")
else:
    print("Error: No se encontró data en el DataFrame.")
