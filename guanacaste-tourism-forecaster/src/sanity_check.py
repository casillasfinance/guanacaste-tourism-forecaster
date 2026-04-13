import pandas as pd

df = pd.read_csv('data/merged/master_tourism_data.csv')
df['DATE'] = pd.to_datetime(df['DATE'])

print('=== DATASET MAESTRO ===')
print(f'Rango: {df.DATE.min().strftime("%b %Y")} -> {df.DATE.max().strftime("%b %Y")}')
print(f'Filas: {len(df)} meses | Columnas: {df.shape[1]}')
print()
print('=== COLUMNAS Y NULOS ===')
for col in df.columns:
    nulls = df[col].isna().sum()
    pct = nulls/len(df)*100
    status = 'OK' if pct < 5 else 'REVISAR'
    print(f'  {col:<35} Nulos: {nulls:>3} ({pct:>4.1f}%)  {status}')
print()
print('=== LLEGADAS (ultimos 6 meses) ===')
print(df[['DATE','Arrivals_sjo','Arrivals_lir']].tail(6).to_string(index=False))
print()
print('=== MACRO (ultimos 3 meses) ===')
print(df[['DATE','tasa_desempleo_usa','inflacion_usa_cpi','precio_petroleo_wti']].tail(3).to_string(index=False))
