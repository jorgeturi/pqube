import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

# ==========================================================
# CARGA DE DATOS
# ==========================================================
df = pd.read_csv("predicciones.csv")
df["hora"] = pd.to_datetime(df["hora"], errors="coerce")

# ==========================================================
# APLICACIÓN DASH
# ==========================================================
app = Dash(__name__)
app.title = "Visualizador de Predicciones"

modelos = sorted(df["id_modelo"].unique())

# ==========================================================
# LAYOUT
# ==========================================================
app.layout = html.Div([
    html.H2("Visualizador Interactivo de Modelos de Predicción", style={"textAlign": "center"}),

    html.Div([
        html.Label("Seleccionar modelo:"),
        dcc.Dropdown(
            id="modelo_dropdown",
            options=[{"label": m, "value": m} for m in modelos],
            value=modelos[0],
            clearable=False,
            style={"width": "300px"}
        ),
    ], style={"textAlign": "center", "margin": "20px"}),

    html.Div([
        html.Label("Rango de fechas:"),
        dcc.DatePickerRange(
            id="rango_fechas",
            start_date=df["hora"].min(),
            end_date=df["hora"].max(),
            display_format="YYYY-MM-DD"
        )
    ], style={"textAlign": "center", "marginBottom": "30px"}),

    dcc.Graph(id="grafico_predicciones", style={"height": "70vh"}),

    html.Div(id="info_click", style={"textAlign": "center", "marginTop": "10px", "fontStyle": "italic"})
])

# ==========================================================
# CALLBACK PRINCIPAL
# ==========================================================
@app.callback(
    Output("grafico_predicciones", "figure"),
    Output("info_click", "children"),
    Input("modelo_dropdown", "value"),
    Input("rango_fechas", "start_date"),
    Input("rango_fechas", "end_date"),
    Input("grafico_predicciones", "clickData")
)
def actualizar_grafico(id_modelo, fecha_inicio, fecha_fin, click_data):
    df_sel = df[(df["id_modelo"] == id_modelo) &
                (df["hora"] >= fecha_inicio) &
                (df["hora"] <= fecha_fin)].copy()

    pasos = sorted(df_sel["paso"].unique())
    df_p1 = df_sel[df_sel["paso"] == 1].copy()

    # === Tooltip general para paso 1 ===
    tooltips = []
    for hora in df_p1["hora"]:
        subset = df_sel[df_sel["hora"] == hora].sort_values("paso")
        texto = "<b>Predicciones multi-step:</b><br>" + "<br>".join(
            [f"Paso {int(p)} ➜ {v:.3f}" for p, v in zip(subset["paso"], subset["prediccion"])]
        )
        tooltips.append(texto)
    df_p1["tooltip"] = tooltips

    # === Figura inicial ===
    fig = go.Figure()

    # Paso 1 (base)
    fig.add_trace(go.Scatter(
        x=df_p1["hora"],
        y=df_p1["prediccion"],
        mode="lines+markers",
        name=f"{id_modelo} (Paso 1)",
        text=df_p1["tooltip"],
        hoverinfo="text+x+y",
        marker=dict(size=7, color="blue"),
        line=dict(color="blue", width=2)
    ))

    # Si hay dato real
    if "real" in df_sel.columns:
        fig.add_trace(go.Scatter(
            x=df_sel["hora"],
            y=df_sel["real"],
            mode="lines",
            name="Valor real",
            line=dict(color="black", width=1)
        ))

    mensaje = "Hacé click sobre una predicción para ver sus pasos futuros."
    # === Si el usuario hizo click en un punto ===
    if click_data:
        hora_click = pd.to_datetime(click_data["points"][0]["x"])
        subset = df_sel[df_sel["hora"] == hora_click].sort_values("paso")

        if len(subset) > 1:
            fig.add_trace(go.Scatter(
                x=subset["hora"] + pd.to_timedelta(subset["paso"] - 1, unit="h"),
                y=subset["prediccion"],
                mode="lines+markers",
                name=f"Trayectoria desde {hora_click.strftime('%Y-%m-%d %H:%M')}",
                line=dict(color="red", width=2, dash="dot"),
                marker=dict(color="red", size=6, symbol="circle"),
                hovertemplate="<b>Paso %{text}</b><br>Predicción=%{y:.3f}",
                text=subset["paso"]
            ))
            mensaje = f"Mostrando predicción multi-step desde {hora_click.strftime('%Y-%m-%d %H:%M')}."
        else:
            mensaje = f"No hay pasos adicionales para {hora_click.strftime('%Y-%m-%d %H:%M')}."

    # Configuración final
    fig.update_layout(
        title=f"Modelo {id_modelo} — Predicciones interactivas",
        xaxis_title="Hora",
        yaxis_title="Valor",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(x=0, y=1.1, orientation="h")
    )

    return fig, mensaje


# ==========================================================
# EJECUCIÓN LOCAL
# ==========================================================
if __name__ == "__main__":
    app.run_server(debug=True, port=8850)
