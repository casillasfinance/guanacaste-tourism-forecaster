import pdfplumber

pdf_llegadas = r"c:\Users\franc\Downloads\guanacaste-tourism-forecaster\guanacaste-tourism-forecaster\data\raw\2026-02_Llegadas_internacionales.pdf"
pdf_ocupacion = r"c:\Users\franc\Downloads\guanacaste-tourism-forecaster\guanacaste-tourism-forecaster\data\raw\Indicadores_BCCR_2018-2024 (Ocupacion hotelera).pdf"

def extract_data_tables(pdf_path, name):
    print(f"\n--- BUSCANDO DATOS EN {name} ---")
    data_found = False
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for t_idx, table in enumerate(tables):
                    if len(table) > 3: # Ignore tiny metadata tables
                        first_row_str = ' '.join(str(item) for item in table[0]).lower()
                        # Check if it looks like a data table (years, months, values etc)
                        if '20' in first_row_str or 'mes' in first_row_str or len(table) > 10:
                            print(f"\n[Pagina {i+1} | Tabla {t_idx+1}] Parece ser de datos con {len(table)} filas.")
                            for row in table[:10]: # Print first 10 rows
                                print(row)
                            data_found = True
        if not data_found:
            print("No se encontró ninguna tabla que parezca contener la data real.")
            # Print text of page 2 or 3
            if len(pdf.pages) > 1:
                print("Texto de la pagina 2:")
                print(pdf.pages[1].extract_text()[:500])
    except Exception as e:
        print(f"Error: {e}")

extract_data_tables(pdf_llegadas, "LLEGADAS INTERNACIONALES")
extract_data_tables(pdf_ocupacion, "OCUPACIÓN HOTELERA BCCR")
