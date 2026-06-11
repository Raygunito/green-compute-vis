import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Data Centers Mondiaux",
    page_icon="🌐",
    layout="wide",
)


def load_css() -> None:
    """Load custom CSS from src/style.css and inject into the Streamlit app."""
    css_path = Path(__file__).resolve().parent / "style.css"
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# ── Normalisation pays ────────────────────────────────────────────────────────

COUNTRY_NORMALIZE = {
    "Canadá": "Canada",
    "México": "Mexico",
    "Países Bajos": "Netherlands",
    "Japón": "Japan",
    "Türkiye": "Turkey",
    "Côte d'Ivoire": "Ivory Coast",
    "Bélgica": "Belgium",
}

# Coordonnées centroïdes pays (lat, lon)
COUNTRY_COORDS = {
    "United States": (37.09, -95.71),
    "United Kingdom": (55.37, -3.43),
    "Germany": (51.16, 10.45),
    "France": (46.22, 2.21),
    "China": (35.86, 104.19),
    "Netherlands": (52.13, 5.29),
    "Canada": (56.13, -106.34),
    "Australia": (-25.27, 133.77),
    "India": (20.59, 78.96),
    "Brazil": (-14.23, -51.92),
    "Italy": (41.87, 12.56),
    "Japan": (36.20, 138.25),
    "Spain": (40.46, -3.74),
    "Indonesia": (-0.78, 113.92),
    "Switzerland": (46.81, 8.22),
    "Sweden": (60.12, 18.64),
    "Russia": (61.52, 105.31),
    "Singapore": (1.35, 103.81),
    "South Africa": (-30.55, 22.93),
    "Malaysia": (4.21, 101.97),
    "Hong Kong": (22.39, 114.10),
    "Poland": (51.91, 19.14),
    "Ireland": (53.41, -8.24),
    "New Zealand": (-40.90, 174.88),
    "Belgium": (50.50, 4.46),
    "Austria": (47.51, 14.55),
    "South Korea": (35.90, 127.76),
    "Denmark": (56.26, 9.50),
    "Norway": (60.47, 8.46),
    "Finland": (61.92, 25.74),
    "Mexico": (23.63, -102.55),
    "Portugal": (39.39, -8.22),
    "Bulgaria": (42.73, 25.48),
    "Chile": (-35.67, -71.54),
    "Thailand": (15.87, 100.99),
    "Israel": (31.04, 34.85),
    "Saudi Arabia": (23.88, 45.07),
    "Argentina": (-38.41, -63.61),
    "Colombia": (4.57, -74.29),
    "Romania": (45.94, 24.96),
    "Turkey": (38.96, 35.24),
    "Vietnam": (14.05, 108.27),
    "Nigeria": (9.08, 8.67),
    "Mexico": (23.63, -102.55),
    "Ukraine": (48.37, 31.16),
    "Czech Republic": (49.81, 15.47),
    "Greece": (39.07, 21.82),
    "Pakistan": (30.37, 69.34),
    "Philippines": (12.87, 121.77),
    "Egypt": (26.82, 30.80),
    "Hungary": (47.16, 19.50),
    "United Arab Emirates": (23.42, 53.84),
    "Bangladesh": (23.68, 90.35),
    "Morocco": (31.79, -7.09),
    "Kenya": (-0.02, 37.90),
    "Slovakia": (48.66, 19.69),
    "Croatia": (45.10, 15.20),
    "Luxembourg": (49.81, 6.12),
    "Serbia": (44.01, 21.00),
    "Qatar": (25.35, 51.18),
    "Kuwait": (29.31, 47.48),
    "Tanzania": (-6.36, 34.89),
    "Ethiopia": (9.14, 40.49),
    "Ghana": (7.94, -1.02),
    "Peru": (-9.18, -75.01),
    "Ecuador": (-1.83, -78.18),
    "Kazakhstan": (48.01, 66.92),
    "Belarus": (53.70, 27.95),
    "Lithuania": (55.16, 23.88),
    "Latvia": (56.87, 24.60),
    "Estonia": (58.59, 25.01),
    "Slovenia": (46.15, 14.99),
    "Ivory Coast": (7.54, -5.54),
    "Taiwan": (23.69, 120.96),
    "Algeria": (28.03, 1.65),
    "Tunisia": (33.88, 9.53),
    "Jordan": (30.58, 36.23),
    "Lebanon": (33.85, 35.86),
    "Oman": (21.51, 55.92),
    "Bahrain": (26.00, 50.55),
    "Sri Lanka": (7.87, 80.77),
    "Nepal": (28.39, 84.12),
    "Myanmar": (16.87, 96.19),
    "Cambodia": (12.56, 104.99),
    "Uruguay": (-32.52, -55.76),
    "Venezuela": (6.42, -66.58),
    "Guatemala": (15.78, -90.23),
    "Zimbabwe": (-19.01, 29.15),
    "Zambia": (-13.13, 27.84),
    "Uganda": (1.37, 32.29),
    "Mozambique": (-18.66, 35.52),
    "Senegal": (14.49, -14.45),
    "Cameroon": (3.84, 11.50),
    "Iceland": (64.96, -19.02),
    "Cyprus": (35.12, 33.43),
    "Malta": (35.93, 14.37),
    "North Macedonia": (41.60, 21.74),
    "Albania": (41.15, 20.17),
    "Bosnia and Herzegovina": (43.91, 17.67),
    "Moldova": (47.41, 28.36),
    "Armenia": (40.06, 45.03),
    "Georgia": (42.31, 43.35),
    "Azerbaijan": (40.14, 47.57),
    "Uzbekistan": (41.37, 64.58),
    "Iraq": (33.22, 43.67),
    "Iran": (32.42, 53.68),
}

# ── Chargement & nettoyage données ───────────────────────────────────────────


@st.cache_data
def load_data():
    df = pd.read_csv("data/data_center_hybrid.csv")

    # Normaliser les noms de pays
    df["Country"] = df["Country"].replace(COUNTRY_NORMALIZE)

    # Filtrer les lignes avec un vrai nom de pays (count > 50 dans le dataset brut)
    vc = df["Country"].value_counts()
    real_countries = vc[vc > 50].index.tolist()
    real_countries = [c for c in real_countries if c != "Unknown"]
    df = df[df["Country"].isin(real_countries)].copy()

    # Ajouter coordonnées
    df["lat"] = df["Country"].map(lambda c: COUNTRY_COORDS.get(c, (None, None))[0])
    df["lon"] = df["Country"].map(lambda c: COUNTRY_COORDS.get(c, (None, None))[1])

    return df


df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Filtres")
    st.markdown("---")

    years = sorted(df["Year"].unique())
    year_range = st.slider(
        "Période",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years))),
    )

    facility_types = sorted(df["Facility_Type"].unique())
    selected_types = st.multiselect(
        "Type de facility",
        options=facility_types,
        default=facility_types,
    )

    cooling_types = sorted(df["Cooling_System_Type"].unique())
    selected_cooling = st.multiselect(
        "Système de refroidissement",
        options=cooling_types,
        default=cooling_types,
    )


# ── Filtrage ──────────────────────────────────────────────────────────────────

mask = (
    df["Year"].between(*year_range)
    & df["Facility_Type"].isin(selected_types)
    & df["Cooling_System_Type"].isin(selected_cooling)
)
dff = df[mask]

# ── En-tête ───────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="main-title">Efficacité des Data Centers Mondiaux</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Refroidissement, énergie et eau : les arbitrages derrière chaque data center</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="research-question">'
    "Le choix du système de refroidissement détermine-t-il à lui seul "
    "l'efficacité énergétique et hydrique d'un data center "
    "et où dans le monde ces arbitrages se manifestent-ils ?"
    "</div>",
    unsafe_allow_html=True,
)

# ── KPIs ──────────────────────────────────────────────────────────────────────

n_facilities = dff["Facility_ID"].nunique()
pue_mean = dff["PUE"].mean()
pct_high_stress = (dff["Surrounding_Water_Stress_Tier"] == "High").mean() * 100
wue_median = dff["WUE_L_per_kWh"].median()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
    <div class="kpi-block">
      <div class="kpi-value">{n_facilities}</div>
      <div class="kpi-label">Facilities analysées</div>
    </div>""",
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
    <div class="kpi-block">
      <div class="kpi-value">{pue_mean:.3f}</div>
      <div class="kpi-label">PUE moyen (énergie)</div>
    </div>""",
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
    <div class="kpi-block">
      <div class="kpi-value">{wue_median:.2f} L</div>
      <div class="kpi-label">WUE médian / kWh</div>
    </div>""",
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f"""
    <div class="kpi-block">
      <div class="kpi-value">{pct_high_stress:.1f}%</div>
      <div class="kpi-label">En zone de stress hydrique élevé</div>
    </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📖 Définitions PUE & WUE"):
    col_def1, col_def2 = st.columns(2)
    with col_def1:
        st.markdown(
            "**PUE — Power Usage Effectiveness**  \n"
            "Ratio entre l'énergie totale consommée par le data center et l'énergie "
            "effectivement utilisée par les serveurs. "
        )
    with col_def2:
        st.markdown(
            "**WUE — Water Usage Effectiveness**  \n"
            "Volume d'eau consommé (en litres) pour produire 1 kWh d'énergie utile aux serveurs. "
        )

# ── Section Focus Chart ───────────────────────────────────────────────────────

st.markdown(
    '<div class="section-title">Efficacité énergétique × hydrique par combinaison de refroidissement</div>',
    unsafe_allow_html=True,
)

# Agrégation heatmap
heatmap_data = (
    dff.groupby(["Cooling_System_Type", "Facility_Type"])
    .agg(
        PUE_mean=("PUE", "mean"),
        WUE_median=("WUE_L_per_kWh", "median"),
        n_facilities=("Facility_ID", "nunique"),
    )
    .reset_index()
)
heatmap_data["WUE_label"] = heatmap_data["WUE_median"].map(lambda x: f"WUE {x:.2f}")
heatmap_data["tooltip_facilities"] = heatmap_data["n_facilities"].map(
    lambda x: f"{x:,} facilities"
)

# Ordre des axes — meilleurs PUE/WUE en bas, pires en haut (cohérence avec légende vert bas / rouge haut)
cooling_order = ["Liquid Cooled", "Air Cooled", "Evaporative"]
facility_order = ["Enterprise/Standard", "Colocation", "Hyperscale/AI"]

# Sélection interactive
selection = alt.selection_point(
    fields=["Cooling_System_Type", "Facility_Type"], toggle=False
)

# Rectangles (fond coloré par PUE)
rect = (
    alt.Chart(heatmap_data)
    .mark_rect(stroke="white", strokeWidth=3, cornerRadius=4)
    .encode(
        x=alt.X(
            "Cooling_System_Type:N",
            sort=cooling_order,
            axis=alt.Axis(
                title="Système de refroidissement",
                labelFontSize=13,
                titleFontSize=13,
                titleFontWeight="normal",
                titleColor="#64748b",
                labelColor="#f1f5f9",
                orient="bottom",
                labelAngle=0,
            ),
        ),
        y=alt.Y(
            "Facility_Type:N",
            sort=facility_order,
            axis=alt.Axis(
                title=None,
                labelFontSize=13,
                labelColor="#f1f5f9",
            ),
        ),
        color=alt.Color(
            "PUE_mean:Q",
            scale=alt.Scale(
                range=["#4ade80", "#facc15", "#f87171"],
                domain=[1.1, 2.0],
            ),
            legend=alt.Legend(
                title="PUE moyen",
                titleFontSize=11,
                titleColor="#94a3b8",
                labelFontSize=10,
                labelColor="#94a3b8",
                orient="right",
                direction="vertical",
                gradientLength=120,
            ),
        ),
        opacity=alt.condition(selection, alt.value(1.0), alt.value(0.55)),
        tooltip=[
            alt.Tooltip("Cooling_System_Type:N", title="Refroidissement"),
            alt.Tooltip("Facility_Type:N", title="Type de facility"),
            alt.Tooltip("PUE_mean:Q", title="PUE moyen", format=".3f"),
            alt.Tooltip("WUE_median:Q", title="WUE médian (L/kWh)", format=".3f"),
            alt.Tooltip("tooltip_facilities:N", title="Nb facilities"),
        ],
    )
    .add_params(selection)
)

# Texte WUE médian
text_wue = (
    alt.Chart(heatmap_data)
    .mark_text(fontSize=14, fontWeight="bold", color="white", dy=-8)
    .encode(
        x=alt.X("Cooling_System_Type:N", sort=cooling_order),
        y=alt.Y("Facility_Type:N", sort=facility_order),
        text=alt.Text("WUE_label:N"),
        opacity=alt.condition(selection, alt.value(1.0), alt.value(0.6)),
    )
)

# Texte nb facilities
text_count = (
    alt.Chart(heatmap_data)
    .mark_text(fontSize=11, color="white", fontWeight="normal", dy=10)
    .encode(
        x=alt.X("Cooling_System_Type:N", sort=cooling_order),
        y=alt.Y("Facility_Type:N", sort=facility_order),
        text=alt.Text("tooltip_facilities:N"),
        opacity=alt.condition(selection, alt.value(0.9), alt.value(0.5)),
    )
)

heatmap_chart = (
    (rect + text_wue + text_count)
    .properties(width=620, height=320, background="transparent")
    .configure_view(strokeWidth=0, fill="transparent")
    .configure_axis(grid=False)
)

# Affichage centré
col_left, col_center, col_right = st.columns([1, 3, 1])
with col_center:
    event = st.altair_chart(
        heatmap_chart, use_container_width=False, on_select="rerun", key="heatmap"
    )

# ── Section Carte ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="section-title">Distribution géographique</div>', unsafe_allow_html=True
)

# Lire la sélection
selected_cooling_val = None
selected_facility_val = None

if event and event.get("selection") and event["selection"].get("param_1"):
    sel = event["selection"]["param_1"]
    if sel:
        selected_cooling_val = sel[0].get("Cooling_System_Type")
        selected_facility_val = sel[0].get("Facility_Type")
    else:
        selected_cooling_val = None
        selected_facility_val = None

if selected_cooling_val and selected_facility_val:
    st.markdown(
        f'<div class="section-sub">'
        f"Sélection : <b>{selected_cooling_val}</b> × <b>{selected_facility_val}</b> "
        f"</div>",
        unsafe_allow_html=True,
    )
    map_df = dff[
        (dff["Cooling_System_Type"] == selected_cooling_val)
        & (dff["Facility_Type"] == selected_facility_val)
        & dff["lat"].notna()
    ].copy()

    # Agréger par pays — tier majoritaire pour éviter les points superposés
    map_agg = (
        map_df.groupby(["Country", "lat", "lon"])
        .agg(
            n_facilities=("Facility_ID", "nunique"),
            PUE_mean=("PUE", "mean"),
            WUE_median=("WUE_L_per_kWh", "median"),
            capacity_total=("Estimated_Capacity_MW", "sum"),
            Surrounding_Water_Stress_Tier=(
                "Surrounding_Water_Stress_Tier",
                lambda x: x.value_counts().idxmax(),
            ),
        )
        .reset_index()
    )

    # Fond carte monde
    world_url = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
    background = (
        alt.Chart(alt.topo_feature(world_url, "countries"))
        .mark_geoshape(fill="#2d3348", stroke="#1e2130", strokeWidth=0.5)
        .project("naturalEarth1")
    )

    stress_color = alt.Color(
        "Surrounding_Water_Stress_Tier:N",
        scale=alt.Scale(
            domain=["Low", "Medium", "High"],
            range=["#4ade80", "#f59e0b", "#f87171"],
        ),
        legend=alt.Legend(
            title="Stress hydrique",
            titleFontSize=11,
            titleColor="#94a3b8",
            labelFontSize=10,
            labelColor="#94a3b8",
            orient="bottom-right",
        ),
    )

    points = (
        alt.Chart(map_agg)
        .mark_circle(opacity=0.75, stroke="white", strokeWidth=0.8)
        .encode(
            longitude="lon:Q",
            latitude="lat:Q",
            size=alt.Size(
                "capacity_total:Q",
                scale=alt.Scale(range=[40, 800]),
                legend=alt.Legend(
                    title="Capacité totale (MW)",
                    titleFontSize=11,
                    labelFontSize=10,
                    orient="bottom-left",
                ),
            ),
            color=stress_color,
            tooltip=[
                alt.Tooltip("Country:N", title="Pays"),
                alt.Tooltip("n_facilities:Q", title="Nb facilities"),
                alt.Tooltip("PUE_mean:Q", title="PUE moyen", format=".3f"),
                alt.Tooltip("WUE_median:Q", title="WUE médian (L/kWh)", format=".3f"),
                alt.Tooltip(
                    "capacity_total:Q", title="Capacité totale (MW)", format=",.0f"
                ),
                alt.Tooltip("Surrounding_Water_Stress_Tier:N", title="Stress hydrique"),
            ],
        )
        .project("naturalEarth1")
    )

    map_chart = (
        (background + points)
        .properties(width=900, height=440, background="transparent")
        .configure_view(strokeWidth=0, fill="transparent")
        .configure_legend(
            labelColor="#94a3b8",
            titleColor="#94a3b8",
        )
    )

    st.altair_chart(map_chart, use_container_width=True)

else:
    st.markdown(
        '<div class="section-sub">Tous les data centers</div>',
        unsafe_allow_html=True,
    )
    map_df = dff[dff["lat"].notna()].copy()
    map_agg = (
        map_df.groupby(["Country", "lat", "lon"])
        .agg(
            n_facilities=("Facility_ID", "nunique"),
            PUE_mean=("PUE", "mean"),
            WUE_median=("WUE_L_per_kWh", "median"),
            capacity_total=("Estimated_Capacity_MW", "sum"),
            Surrounding_Water_Stress_Tier=(
                "Surrounding_Water_Stress_Tier",
                lambda x: x.value_counts().idxmax(),
            ),
        )
        .reset_index()
    )
    world_url = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
    background = (
        alt.Chart(alt.topo_feature(world_url, "countries"))
        .mark_geoshape(fill="#2d3348", stroke="#1e2130", strokeWidth=0.5)
        .project("naturalEarth1")
    )
    stress_color = alt.Color(
        "Surrounding_Water_Stress_Tier:N",
        scale=alt.Scale(
            domain=["Low", "Medium", "High"],
            range=["#4ade80", "#f59e0b", "#f87171"],
        ),
        legend=alt.Legend(
            title="Stress hydrique",
            titleFontSize=11,
            titleColor="#94a3b8",
            labelFontSize=10,
            labelColor="#94a3b8",
            orient="bottom-right",
        ),
    )
    points = (
        alt.Chart(map_agg)
        .mark_circle(opacity=0.75, stroke="white", strokeWidth=0.8)
        .encode(
            longitude="lon:Q",
            latitude="lat:Q",
            size=alt.Size(
                "capacity_total:Q",
                scale=alt.Scale(range=[40, 800]),
                legend=alt.Legend(
                    title="Capacité totale (MW)",
                    titleFontSize=11,
                    labelFontSize=10,
                    orient="bottom-left",
                ),
            ),
            color=stress_color,
            tooltip=[
                alt.Tooltip("Country:N", title="Pays"),
                alt.Tooltip("n_facilities:Q", title="Nb facilities"),
                alt.Tooltip("PUE_mean:Q", title="PUE moyen", format=".3f"),
                alt.Tooltip("WUE_median:Q", title="WUE médian (L/kWh)", format=".3f"),
                alt.Tooltip(
                    "capacity_total:Q", title="Capacité totale (MW)", format=",.0f"
                ),
                alt.Tooltip("Surrounding_Water_Stress_Tier:N", title="Stress hydrique"),
            ],
        )
        .project("naturalEarth1")
    )
    map_chart = (
        (background + points)
        .properties(width=900, height=440, background="transparent")
        .configure_view(strokeWidth=0, fill="transparent")
        .configure_legend(labelColor="#94a3b8", titleColor="#94a3b8")
    )
    st.altair_chart(map_chart, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<div style='font-size:0.75rem;color:#94a3b8;text-align:center;'>"
    "Master 2 IASD — Université Paris-Dauphine · Cours de Visualisation de Données · 2025"
    "</div>",
    unsafe_allow_html=True,
)
