import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import os

# ── Load & preprocess data ─────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
df = pd.read_parquet(os.path.join(BASE, "data_2019.parquet"))

MONTH_NAMES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}
AGE_LABELS = {
    0: "< 1 año", 1: "1-4", 2: "5-9", 3: "10-14", 5: "15-19",
    6: "20-24", 7: "25-29", 8: "30-34", 9: "35-39", 10: "40-44",
    11: "45-49", 12: "50-54", 13: "55-59", 14: "60-64", 15: "65-69",
    16: "70-74", 17: "75-79", 18: "80-84", 19: "85-89", 20: "90-94",
    21: "95-99", 22: "100+",
}
SITIO_LABELS = {
    1: "Hospital público", 2: "Hospital privado", 3: "Domicilio",
    4: "Vía pública", 5: "Otro", 6: "En tránsito", 9: "Sin dato",
}
AREA_LABELS = {1: "Cabecera municipal", 2: "Centro poblado", 3: "Rural disperso", 9: "Sin dato"}

df["MES_NOMBRE"] = df["MES"].map(MONTH_NAMES)
df["EDAD_LABEL"] = df["GRUPO_EDAD1"].map(AGE_LABELS)
df["SITIO_LABEL"] = df["SITIO_DEFUNCION"].map(SITIO_LABELS).fillna("Sin dato")
df["AREA_LABEL"] = df["AREA_DEFUNCION"].map(AREA_LABELS).fillna("Sin dato")

DEPTOS = sorted(df["DEPARTAMENTO"].unique())
TOTAL = len(df)

# ── Color palette ───────────────────────────────────────────────────────────
COLORS = {
    "bg": "#0f172a",
    "surface": "#1e293b",
    "border": "#334155",
    "primary": "#38bdf8",
    "secondary": "#818cf8",
    "accent": "#f472b6",
    "success": "#34d399",
    "warning": "#fbbf24",
    "text": "#e2e8f0",
    "muted": "#94a3b8",
}
PALETTE = ["#38bdf8", "#818cf8", "#f472b6", "#34d399", "#fbbf24", "#fb923c", "#a78bfa", "#2dd4bf"]

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
    yaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=COLORS["border"]),
    hoverlabel=dict(bgcolor=COLORS["surface"], bordercolor=COLORS["border"], font_color=COLORS["text"]),
)

# ── App ─────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    title="Mortalidad Colombia 2019",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server  # for Gunicorn / PaaS

# ── KPI card helper ─────────────────────────────────────────────────────────
def kpi_card(title, value, subtitle="", color=COLORS["primary"]):
    return html.Div(
        [
            html.P(title, style={"margin": 0, "fontSize": "0.75rem", "color": COLORS["muted"], "textTransform": "uppercase", "letterSpacing": "0.05em"}),
            html.H2(value, style={"margin": "4px 0", "fontSize": "2rem", "fontWeight": 700, "color": color}),
            html.P(subtitle, style={"margin": 0, "fontSize": "0.75rem", "color": COLORS["muted"]}),
        ],
        style={
            "background": COLORS["surface"],
            "border": f"1px solid {COLORS['border']}",
            "borderRadius": "12px",
            "padding": "20px 24px",
            "flex": "1",
            "minWidth": "160px",
        },
    )


# ── Layout ───────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={"background": COLORS["bg"], "minHeight": "100vh", "fontFamily": "Inter, sans-serif", "color": COLORS["text"]},
    children=[
        # Header
        html.Div(
            style={"background": COLORS["surface"], "borderBottom": f"1px solid {COLORS['border']}", "padding": "16px 32px"},
            children=[
                html.H1("🏥 Mortalidad en Colombia — 2019", style={"margin": 0, "fontSize": "1.5rem", "fontWeight": 700}),
                html.P("Análisis interactivo de defunciones no fetales · Fuente: DANE", style={"margin": "4px 0 0", "color": COLORS["muted"], "fontSize": "0.85rem"}),
            ],
        ),

        html.Div(
            style={"padding": "24px 32px"},
            children=[

                # ── Filters ──────────────────────────────────────────────────
                html.Div(
                    style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px", "alignItems": "flex-end"},
                    children=[
                        html.Div([
                            html.Label("Departamento", style={"fontSize": "0.8rem", "color": COLORS["muted"]}),
                            dcc.Dropdown(
                                id="filter-depto",
                                options=[{"label": "Todos los departamentos", "value": "ALL"}] + [{"label": d, "value": d} for d in DEPTOS],
                                value="ALL",
                                clearable=False,
                                style={"minWidth": "240px", "background": COLORS["surface"], "color": "#000"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Sexo", style={"fontSize": "0.8rem", "color": COLORS["muted"]}),
                            dcc.Dropdown(
                                id="filter-sexo",
                                options=[
                                    {"label": "Todos", "value": "ALL"},
                                    {"label": "Masculino", "value": "Masculino"},
                                    {"label": "Femenino", "value": "Femenino"},
                                ],
                                value="ALL",
                                clearable=False,
                                style={"minWidth": "160px", "color": "#000"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Rango de meses", style={"fontSize": "0.8rem", "color": COLORS["muted"]}),
                            dcc.RangeSlider(id="filter-mes", min=1, max=12, step=1, value=[1, 12],
                                marks={m: MONTH_NAMES[m] for m in range(1, 13)},
                                tooltip={"placement": "bottom"},
                                ),
                        ], style={"minWidth": "320px"}),
                    ],
                ),

                # ── KPIs ─────────────────────────────────────────────────────
                html.Div(id="kpi-row", style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"}),

                # ── Row 1: Tiempo + Departamentos ─────────────────────────────
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                    children=[
                        html.Div(
                            [html.H3("Defunciones por mes", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-mes", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                        html.Div(
                            [html.H3("Top 10 departamentos", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-depto", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                    ],
                ),

                # ── Row 2: Causas + Manera ─────────────────────────────────
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                    children=[
                        html.Div(
                            [html.H3("Top 15 causas de muerte (CIE-10)", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-causas", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                        html.Div(
                            [html.H3("Distribución por manera de muerte", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-manera", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                    ],
                ),

                # ── Row 3: Sexo + Edad ─────────────────────────────────────
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 2fr", "gap": "16px", "marginBottom": "16px"},
                    children=[
                        html.Div(
                            [html.H3("Por sexo", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-sexo", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                        html.Div(
                            [html.H3("Pirámide poblacional de muertes", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-piramide", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                    ],
                ),

                # ── Row 4: Sitio + Área + Nivel educativo ─────────────────
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                    children=[
                        html.Div(
                            [html.H3("Sitio de defunción", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-sitio", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                        html.Div(
                            [html.H3("Área de defunción", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-area", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                        html.Div(
                            [html.H3("Manera de muerte por sexo", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                             dcc.Graph(id="chart-manera-sexo", config={"displayModeBar": False})],
                            style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}"},
                        ),
                    ],
                ),

                # ── Row 5: Heatmap mes x depto ────────────────────────────
                html.Div(
                    [html.H3("Mapa de calor: defunciones por mes y departamento", style={"margin": "0 0 8px", "fontSize": "1rem"}),
                     dcc.Graph(id="chart-heatmap", config={"displayModeBar": False})],
                    style={"background": COLORS["surface"], "borderRadius": "12px", "padding": "20px", "border": f"1px solid {COLORS['border']}", "marginBottom": "16px"},
                ),

                # Footer
                html.P("Datos: DANE — Estadísticas Vitales Colombia 2019 · Desarrollado con Plotly Dash · Python",
                       style={"textAlign": "center", "color": COLORS["muted"], "fontSize": "0.75rem", "paddingTop": "16px"}),
            ],
        ),
    ],
)


# ── Callbacks ────────────────────────────────────────────────────────────────
def apply_filters(depto, sexo, mes_range):
    dff = df.copy()
    if depto != "ALL":
        dff = dff[dff["DEPARTAMENTO"] == depto]
    if sexo != "ALL":
        dff = dff[dff["SEXO_LABEL"] == sexo]
    dff = dff[(dff["MES"] >= mes_range[0]) & (dff["MES"] <= mes_range[1])]
    return dff


@callback(Output("kpi-row", "children"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def update_kpis(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    n = len(dff)
    natural_pct = f"{100*len(dff[dff['MANERA_MUERTE']=='Natural'])/n:.1f}%" if n else "–"
    top_causa = dff["DESC_CAUSA"].value_counts().index[0][:30] + "…" if n else "–"
    hom = len(dff[dff["MANERA_MUERTE"] == "Homicidio"])
    return [
        kpi_card("Total defunciones", f"{n:,}", f"de {TOTAL:,} nacional", COLORS["primary"]),
        kpi_card("Muertes naturales", natural_pct, "del total filtrado", COLORS["success"]),
        kpi_card("Homicidios", f"{hom:,}", f"{100*hom/n:.1f}% del filtrado" if n else "", COLORS["accent"]),
        kpi_card("Principal causa", top_causa, "código CIE-10", COLORS["warning"]),
    ]


@callback(Output("chart-mes", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_mes(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff.groupby("MES").size().reset_index(name="Defunciones")
    g["Mes"] = g["MES"].map(MONTH_NAMES)
    fig = px.bar(g, x="Mes", y="Defunciones", color="Defunciones",
                 color_continuous_scale=["#1e3a5f", COLORS["primary"]])
    fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False,
                      title=dict(text="", x=0))
    fig.update_traces(marker_line_width=0)
    return fig


@callback(Output("chart-depto", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_depto(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff.groupby("DEPARTAMENTO").size().reset_index(name="Defunciones").nlargest(10, "Defunciones")
    fig = px.bar(g.sort_values("Defunciones"), x="Defunciones", y="DEPARTAMENTO",
                 orientation="h", color="Defunciones",
                 color_continuous_scale=["#2d1b69", COLORS["secondary"]])
    fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, yaxis_title="")
    fig.update_traces(marker_line_width=0)
    return fig


@callback(Output("chart-causas", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_causas(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff.groupby("DESC_CAUSA").size().reset_index(name="N").nlargest(15, "N")
    g["DESC_CORTA"] = g["DESC_CAUSA"].str[:40]
    fig = px.bar(g.sort_values("N"), x="N", y="DESC_CORTA", orientation="h",
                 color="N", color_continuous_scale=["#1e3a5f", COLORS["primary"]],
                 hover_data={"DESC_CAUSA": True, "DESC_CORTA": False})
    fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, yaxis_title="", height=420)
    fig.update_traces(marker_line_width=0)
    return fig


@callback(Output("chart-manera", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_manera(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff["MANERA_MUERTE"].value_counts().reset_index()
    g.columns = ["Manera", "N"]
    fig = px.pie(g, names="Manera", values="N", hole=0.45,
                 color_discrete_sequence=PALETTE)
    fig.update_layout(**PLOT_LAYOUT)
    fig.update_traces(textposition="outside", textinfo="label+percent")
    return fig


@callback(Output("chart-sexo", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_sexo(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff["SEXO_LABEL"].value_counts().reset_index()
    g.columns = ["Sexo", "N"]
    fig = px.pie(g, names="Sexo", values="N", hole=0.55,
                 color_discrete_map={"Masculino": COLORS["primary"], "Femenino": COLORS["accent"], "Indeterminado": COLORS["muted"]})
    fig.update_layout(**PLOT_LAYOUT)
    fig.update_traces(textinfo="label+percent")
    return fig


@callback(Output("chart-piramide", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_piramide(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    age_order = list(AGE_LABELS.values())
    g = dff[dff["SEXO_LABEL"].isin(["Masculino", "Femenino"])]
    g = g.groupby(["EDAD_LABEL", "SEXO_LABEL"]).size().reset_index(name="N")
    g = g[g["EDAD_LABEL"].notna()]

    masc = g[g["SEXO_LABEL"] == "Masculino"]
    fem = g[g["SEXO_LABEL"] == "Femenino"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=masc["EDAD_LABEL"], x=-masc["N"], orientation="h",
        name="Masculino", marker_color=COLORS["primary"], hovertemplate="%{y}: %{customdata:,}<extra>Masculino</extra>",
        customdata=masc["N"],
    ))
    fig.add_trace(go.Bar(
        y=fem["EDAD_LABEL"], x=fem["N"], orientation="h",
        name="Femenino", marker_color=COLORS["accent"], hovertemplate="%{y}: %{x:,}<extra>Femenino</extra>",
    ))
    fig.update_layout(
        **PLOT_LAYOUT, barmode="overlay",
        xaxis=dict(tickformat=",.0f", gridcolor=COLORS["border"],
                   tickvals=[-30000, -20000, -10000, 0, 10000, 20000, 30000],
                   ticktext=["30k", "20k", "10k", "0", "10k", "20k", "30k"]),
        bargap=0.1, height=420,
    )
    return fig


@callback(Output("chart-sitio", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_sitio(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff["SITIO_LABEL"].value_counts().reset_index()
    g.columns = ["Sitio", "N"]
    fig = px.bar(g.sort_values("N"), x="N", y="Sitio", orientation="h",
                 color="N", color_continuous_scale=["#1a3a2a", COLORS["success"]])
    fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, yaxis_title="")
    fig.update_traces(marker_line_width=0)
    return fig


@callback(Output("chart-area", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_area(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff["AREA_LABEL"].value_counts().reset_index()
    g.columns = ["Área", "N"]
    fig = px.pie(g, names="Área", values="N", hole=0.45,
                 color_discrete_sequence=[COLORS["warning"], COLORS["secondary"], COLORS["accent"], COLORS["muted"]])
    fig.update_layout(**PLOT_LAYOUT)
    fig.update_traces(textinfo="label+percent", textposition="outside")
    return fig


@callback(Output("chart-manera-sexo", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_manera_sexo(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff[dff["SEXO_LABEL"].isin(["Masculino", "Femenino"])]
    g = g.groupby(["MANERA_MUERTE", "SEXO_LABEL"]).size().reset_index(name="N")
    fig = px.bar(g, x="MANERA_MUERTE", y="N", color="SEXO_LABEL",
                 barmode="group",
                 color_discrete_map={"Masculino": COLORS["primary"], "Femenino": COLORS["accent"]},
                 labels={"MANERA_MUERTE": "Manera", "N": "Defunciones", "SEXO_LABEL": "Sexo"})
    fig.update_layout(**PLOT_LAYOUT)
    fig.update_traces(marker_line_width=0)
    return fig


@callback(Output("chart-heatmap", "figure"), Input("filter-depto", "value"), Input("filter-sexo", "value"), Input("filter-mes", "value"))
def chart_heatmap(depto, sexo, mes_range):
    dff = apply_filters(depto, sexo, mes_range)
    g = dff.groupby(["DEPARTAMENTO", "MES"]).size().reset_index(name="N")
    pivot = g.pivot(index="DEPARTAMENTO", columns="MES", values="N").fillna(0)
    pivot.columns = [MONTH_NAMES[c] for c in pivot.columns]

    fig = px.imshow(pivot, aspect="auto",
                    color_continuous_scale=[[0, COLORS["bg"]], [0.3, "#1e3a5f"], [1, COLORS["primary"]]],
                    labels={"color": "Defunciones"})
    fig.update_layout(**PLOT_LAYOUT, height=520,
                      xaxis_title="Mes", yaxis_title="Departamento")
    return fig


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
