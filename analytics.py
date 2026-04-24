import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from models import THEME_COLORS, DISTANCES, DISTANCES_KM

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(26,26,46,0.6)",
    font=dict(color="#E8E8F0", family="Poppins"),
    margin=dict(t=44,b=24,l=20,r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

def build_df(courses):
    return pd.DataFrame(courses) if courses else pd.DataFrame()

def stats_generales(df):
    if df.empty: return {}
    p = df["prix"] if "prix" in df.columns else pd.Series([0])
    return {
        "total":       len(df),
        "disponibles": int((df.statut=="disponible").sum()),
        "en_cours":    int((df.statut=="en_cours").sum()),
        "terminees":   int((df.statut=="terminee").sum()),
        "prix_moyen":  int(p.mean()),
        "prix_max":    int(p.max()),
        "prix_min":    int(p.min()),
        "prix_ecart":  round(float(p.std()),1),
        "prix_median": int(p.median()),
        "prix_q1":     int(p.quantile(0.25)),
        "prix_q3":     int(p.quantile(0.75)),
        "recette":     int(df[df.statut=="terminee"]["prix"].sum()) if "prix" in df.columns else 0,
    }

def _dist_km(label):
    return dict(zip(DISTANCES, DISTANCES_KM)).get(label, 2.0)

def fig_regression(df):
    if df.empty or "prix" not in df.columns or "distance" not in df.columns:
        return None
    df2 = df.copy()
    df2["dist_km"] = df2["distance"].apply(_dist_km)
    x, y = df2["dist_km"].values, df2["prix"].values
    a, b = np.polyfit(x, y, 1)
    xl   = np.linspace(x.min(), x.max(), 100)
    r2   = float(np.corrcoef(x, y)[0,1]**2)
    fig  = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="Observations",
        marker=dict(color=THEME_COLORS[0], size=10, opacity=0.85)))
    fig.add_trace(go.Scatter(x=xl, y=a*xl+b, mode="lines",
        name=f"y = {a:.1f}x + {b:.1f}",
        line=dict(color=THEME_COLORS[2], width=3)))
    fig.update_layout(**LAYOUT, title=f"📈 Régression Linéaire — R² = {r2:.3f}",
        xaxis_title="Distance (km)", yaxis_title="Prix (FCFA)")
    return fig, a, b, r2

def fig_quartiers(df):
    if "depart" not in df.columns or df.empty: return None
    c = df["depart"].value_counts().reset_index()
    c.columns = ["Quartier","Courses"]
    fig = px.bar(c.head(10), x="Courses", y="Quartier", orientation="h",
                 color_discrete_sequence=[THEME_COLORS[0]], title="Top 10 Quartiers de Départ")
    fig.update_layout(**LAYOUT)
    return fig

def fig_meteo(df):
    if "meteo" not in df.columns or df.empty: return None
    c = df["meteo"].value_counts().reset_index()
    c.columns = ["Météo","Courses"]
    fig = px.pie(c, names="Météo", values="Courses",
                 color_discrete_sequence=THEME_COLORS, title="Répartition par Météo")
    fig.update_layout(**LAYOUT)
    return fig

def fig_prix_hist(df):
    if "prix" not in df.columns or df.empty: return None
    fig = px.histogram(df, x="prix", nbins=15,
                       color_discrete_sequence=[THEME_COLORS[1]],
                       title="Distribution des Prix (FCFA)")
    fig.update_layout(**LAYOUT)
    return fig

def fig_trafic(df):
    if "trafic" not in df.columns or df.empty: return None
    c = df["trafic"].value_counts().reset_index()
    c.columns = ["Trafic","Courses"]
    fig = px.bar(c, x="Trafic", y="Courses",
                 color_discrete_sequence=THEME_COLORS, title="État du Trafic")
    fig.update_layout(**LAYOUT)
    return fig

def fig_plage(df):
    if "plage" not in df.columns or df.empty: return None
    c = df["plage"].value_counts().reset_index()
    c.columns = ["Plage","Courses"]
    fig = px.bar(c, x="Plage", y="Courses",
                 color_discrete_sequence=[THEME_COLORS[2]], title="Courses par Plage Horaire")
    fig.update_layout(**LAYOUT)
    return fig

def fig_boxplot(df):
    if "prix" not in df.columns or df.empty: return None
    fig = px.box(df, y="prix", color_discrete_sequence=[THEME_COLORS[3]],
                 title="Boîte à Moustaches — Prix (FCFA)")
    fig.update_layout(**LAYOUT)
    return fig

def fig_statuts(df):
    if "statut" not in df.columns or df.empty: return None
    c = df["statut"].value_counts().reset_index()
    c.columns = ["Statut","Nombre"]
    fig = px.pie(c, names="Statut", values="Nombre",
                 color_discrete_sequence=THEME_COLORS, title="Répartition par Statut")
    fig.update_layout(**LAYOUT)
    return fig