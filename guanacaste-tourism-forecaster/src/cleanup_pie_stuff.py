import json, os

nb_path = 'notebooks/03_data_preparation.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Remove cells injected for historical/pie analysis
ids_to_remove = {'historical_intel_md', 'historical_intel_code'}
nb['cells'] = [c for c in nb['cells'] if c.get('id') not in ids_to_remove]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"✅ Celdas de análisis histórico eliminadas. Total celdas: {len(nb['cells'])}")

# Remove the external HTML file
html_path = 'reports/origin_breakdown_pie.html'
if os.path.exists(html_path):
    os.remove(html_path)
    print("✅ origin_breakdown_pie.html eliminado")

# Remove the injection scripts
for f_path in ['src/inject_historical_analysis.py', 'src/extract_table_numbers.py', 'src/inspect_pdfs.py']:
    if os.path.exists(f_path):
        os.remove(f_path)
        print(f"✅ {f_path} eliminado")

print("\n🚀 Limpieza completa. Listo para modelado.")
