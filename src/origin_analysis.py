import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Datos representativos basados en informes estadísticos del ICT 2024-2025
# Estos porcentajes reflejan el origen de las llegadas internacionales por vía aérea

stats_lir = {
    'Mercado': ['Estados Unidos', 'Canadá', 'Europa', 'Otros'],
    'Llegadas': [725000, 185000, 42000, 19000] # Estimado basado en ~970k ingresos LIR
}

stats_sjo = {
    'Mercado': ['Estados Unidos', 'Europa', 'Sudamérica', 'Canadá', 'Centroamérica/Otros'],
    'Llegadas': [850000, 480000, 290000, 150000, 210000] # Estimado basado en ~1.9M ingresos SJO
}

df_lir = pd.DataFrame(stats_lir)
df_sjo = pd.DataFrame(stats_sjo)

# Crear Subplots de Tortas
fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                    subplot_titles=['<b>Origen: LIR (Guanacaste)</b>', '<b>Origen: SJO (Alajuela)</b>'])

# Gráfico LIR
fig.add_trace(go.Pie(labels=df_lir['Mercado'], values=df_lir['Llegadas'], name="LIR",
                     marker=dict(colors=['#00ff9d', '#00d4ff', '#f9c74f', '#7b2cbf'])), 1, 1)

# Gráfico SJO
fig.add_trace(go.Pie(labels=df_sjo['Mercado'], values=df_sjo['Llegadas'], name="SJO",
                     marker=dict(colors=['#00ff9d', '#f9c74f', '#ff6b35', '#00d4ff', '#7b2cbf'])), 1, 2)

# Estilo Premium
fig.update_traces(hole=.4, hoverinfo="label+percent+name", textinfo='percent+label')

fig.update_layout(
    title_text="<b>Distribución de Turistas por Mercado de Origen (2024 Est.)</b>",
    template='plotly_dark',
    annotations=[dict(text='LIR', x=0.20, y=0.5, font_size=20, showarrow=False),
                 dict(text='SJO', x=0.80, y=0.5, font_size=20, showarrow=False)],
    legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
)

# Guardar demostración para el usuario
fig.write_html('reports/origin_breakdown_pie.html')
fig.show()
