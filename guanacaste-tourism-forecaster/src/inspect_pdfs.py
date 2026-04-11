import pdfplumber

pdf_llegadas = r"c:\Users\franc\Downloads\guanacaste-tourism-forecaster\guanacaste-tourism-forecaster\data\raw\2026-02_Llegadas_internacionales.pdf"

print("--- INSPECCIÓN DETALLADA LLEGADAS ---")
with pdfplumber.open(pdf_llegadas) as pdf:
    print(f"Total páginas: {len(pdf.pages)}")
    for i in range(min(10, len(pdf.pages))):
        print(f"\n--- PAGINA {i+1} ---")
        text = pdf.pages[i].extract_text()
        if text:
            print(text[:1000]) # First 1000 chars
        else:
            print("No text found.")

pdf_ocupacion = r"c:\Users\franc\Downloads\guanacaste-tourism-forecaster\guanacaste-tourism-forecaster\data\raw\Indicadores_BCCR_2018-2024 (Ocupacion hotelera).pdf"
print("\n--- INSPECCIÓN DETALLADA OCUPACIÓN ---")
with pdfplumber.open(pdf_ocupacion) as pdf:
    print(f"Total páginas: {len(pdf.pages)}")
    for i in range(min(5, len(pdf.pages))):
        print(f"\n--- PAGINA {i+1} ---")
        text = pdf.pages[i].extract_text()
        if text:
            print(text[:1000])
        else:
            print("No text found.")
