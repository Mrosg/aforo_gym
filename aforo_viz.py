import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

carpeta = "C:/Users/mrosg/Desktop/Programación/scrapeo_aforo/"

CSV_FILE = f"{carpeta}aforo_dreamfit.csv"

# --- Cargar datos ---
df = pd.read_csv(CSV_FILE)
df["hora"] = pd.to_datetime(df["hora"])
df["personas"] = pd.to_numeric(df["personas"])

# --- Calcular la semana actual (lunes a viernes) ---
hoy = df["hora"].dt.date.max()
hoy_dt = datetime.combine(hoy, datetime.min.time())
lunes = hoy_dt - timedelta(days=hoy_dt.weekday())

dias_semana = [lunes + timedelta(days=i) for i in range(5)]
nombres_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

colores = ["#4C9BE8", "#E8774C", "#4CE87A", "#E8D44C", "#A04CE8"]

# --- Figura ---
fig = go.Figure()

for i, (dia, nombre) in enumerate(zip(dias_semana, nombres_dias)):
    datos_dia = df[df["hora"].dt.date == dia.date()].copy()

    if datos_dia.empty:
        continue

    # Normalizar al lunes para alinear todas las líneas en el mismo eje X
    datos_dia["hora_normalizada"] = datos_dia["hora"].apply(
        lambda t: lunes.replace(hour=t.hour, minute=t.minute, second=0)
    )

    fig.add_trace(go.Scatter(
        x=datos_dia["hora_normalizada"],
        y=datos_dia["personas"],
        mode="lines+markers",
        name=nombre,
        line=dict(color=colores[i], width=2),
        marker=dict(size=4),
        hovertemplate="%{x|%H:%M} — %{y} personas<extra>" + nombre + "</extra>"
    ))

# --- Formato ---
fig.update_layout(
    title=dict(text="Aforo Dreamfit Aluche", font=dict(size=16)),
    xaxis=dict(
        tickformat="%H:%M",
        dtick=15 * 60 * 1000,
        range=[
            lunes.replace(hour=5, minute=30).isoformat(),
            lunes.replace(hour=23, minute=30).isoformat()
        ],
        tickangle=45,
        title="Hora"
    ),
    yaxis=dict(
        range=[0, 400],
        title="Personas"
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    hovermode="x unified",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

fig.update_xaxes(showgrid=True, gridcolor="#eeeeee")
fig.update_yaxes(showgrid=True, gridcolor="#eeeeee")

fig.write_html(f"{carpeta}aforo_semana.html")
fig.show()