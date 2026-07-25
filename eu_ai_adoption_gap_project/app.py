"""Interactive Streamlit dashboard for the EU AI adoption story."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.charts import (
    PURPOSE_LABELS,
    fig_01_eu_acceleration,
    fig_04_size_gap,
    fig_07_sector_growth,
    fig_09_sector_purpose_heatmap,
    fig_10_interest_vs_adoption,
    fig_11_barriers,
)
from src.data import (
    ALL_ACTIVITIES,
    EU,
    EU27_CODES,
    HIGH_LEVEL_SECTORS,
    SECTOR_SHORT,
    SECTOR_SOURCE,
    SIZE_SHORT,
    load_data,
    metric,
)
from src.style import (
    BLUE,
    INK,
    LIGHT,
    MUTED,
    ORANGE,
    VERMILLION,
    apply_layout,
    format_1dp,
)


st.set_page_config(
    page_title="Europe's AI Adoption Gap",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /*
      Keep the main dashboard readable regardless of the visitor's browser or
      Streamlit theme. Streamlit otherwise lets some labels inherit dark-mode
      text colors even though this app uses a white canvas.
    */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #ffffff;
        color: #172033;
    }
    .block-container { max-width: 1280px; padding-top: 2rem; padding-bottom: 4rem; }
    h1, h2, h3 { color: #172033; letter-spacing: -0.02em; }

    /* Summary metric cards */
    [data-testid="stMetric"] {
        background: #f6f8fb;
        border: 1px solid #e8ecf2;
        border-radius: 12px;
        padding: 14px 16px;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #475467 !important;
        opacity: 1 !important;
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div {
        color: #0072b2 !important;
    }
    [data-testid="stMetricDelta"] { opacity: 1 !important; }

    /* Navigation tabs: visible at rest, on hover, and when selected */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        border-bottom-color: #e8ecf2;
    }
    .stTabs button[data-baseweb="tab"] {
        color: #475467 !important;
        opacity: 1 !important;
        padding: 0.55rem 0.75rem !important;
    }
    .stTabs button[data-baseweb="tab"] p {
        color: inherit !important;
        opacity: 1 !important;
    }
    .stTabs button[data-baseweb="tab"]:hover {
        color: #0072b2 !important;
    }
    .stTabs button[data-baseweb="tab"][aria-selected="true"] {
        color: #0072b2 !important;
        font-weight: 600;
    }
    .stTabs button[data-baseweb="tab"]:focus-visible {
        outline: 2px solid #0072b2;
        outline-offset: 2px;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #0072b2 !important;
    }

    .story-note {
        border-left: 4px solid #e69f00;
        background: #fff9ed;
        color: #172033;
        padding: 0.9rem 1rem;
        border-radius: 4px 10px 10px 4px;
        margin: 0.5rem 0 1.25rem 0;
    }
    .story-note * { color: #172033 !important; }
    .small-note { color: #667085; font-size: 0.9rem; }
    [data-testid="stSidebar"] .small-note { color: #aab3c2; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_data()


def country_ranking(
    data: pd.DataFrame, year: int, focus_country: str
) -> go.Figure:
    frame = metric(
        data,
        indicator="E_AI_TANY",
        unit="PC_ENT",
        geo=EU27_CODES,
        size="GE10",
        sector=ALL_ACTIVITIES,
        year=year,
    ).sort_values("value")
    frame["color"] = frame["geo"].map(
        lambda code: VERMILLION if code == focus_country else BLUE
    )
    eu_value = metric(
        data,
        indicator="E_AI_TANY",
        unit="PC_ENT",
        geo=EU,
        size="GE10",
        sector=ALL_ACTIVITIES,
        year=year,
    )["value"].iloc[0]
    focus = frame[frame["geo"].eq(focus_country)].iloc[0]
    rank = int(frame["value"].rank(ascending=False, method="min").loc[focus.name])

    fig = go.Figure(
        go.Bar(
            x=frame["value"],
            y=frame["geo_label"],
            orientation="h",
            marker_color=frame["color"],
            customdata=frame["geo_label"],
            hovertemplate="<b>%{customdata}</b><br>%{x:.1f}% use AI<extra></extra>",
        )
    )
    fig.add_vline(
        x=eu_value,
        line_dash="dot",
        line_color=ORANGE,
        annotation_text=f"EU: {eu_value:.1f}%",
        annotation_position="top",
    )
    fig.update_xaxes(title="Share of enterprises using AI", ticksuffix="%")
    fig.update_yaxes(title=None, tickfont={"size": 10})
    return apply_layout(
        fig,
        title=f"{focus['geo_label']} ranks #{rank} of 27 in {year}",
        subtitle="Country comparison with the selected country highlighted",
        height=720,
        margin={"l": 120, "r": 35, "t": 105, "b": 70},
    )


def country_size_profile(
    data: pd.DataFrame, country: str
) -> go.Figure:
    sizes = ["10-49", "50-249", "GE250"]
    frame = metric(
        data,
        indicator="E_AI_TANY",
        unit="PC_ENT",
        geo=country,
        size=sizes,
        sector=ALL_ACTIVITIES,
        year=[2023, 2024, 2025],
    )
    country_name = frame["geo_label"].iloc[0]
    colors = {"10-49": "#56B4E9", "50-249": "#E69F00", "GE250": "#D55E00"}
    fig = go.Figure()
    for size in sizes:
        part = frame[frame["size_emp"].eq(size)].sort_values("time")
        fig.add_trace(
            go.Scatter(
                x=part["time"],
                y=part["value"],
                mode="lines+markers+text",
                name=SIZE_SHORT[size],
                text=["", "", f"{part['value'].iloc[-1]:.1f}%"],
                textposition="middle right",
                cliponaxis=False,
                line={"width": 3, "color": colors[size]},
                marker={"size": 9, "color": colors[size]},
                hovertemplate=(
                    f"{SIZE_SHORT[size]}<br>%{{x}}: %{{y:.1f}}%<extra></extra>"
                ),
            )
        )
    fig.update_xaxes(
        tickmode="array",
        tickvals=[2023, 2024, 2025],
        range=[2022.85, 2025.35],
        title=None,
    )
    fig.update_yaxes(title="Share using AI", ticksuffix="%", rangemode="tozero")
    return apply_layout(
        fig,
        title=f"{country_name}'s adoption path by firm size",
        subtitle="Use the country selector to compare how the size divide changes over time",
        legend=True,
    )


def sector_purpose_ranking(
    data: pd.DataFrame, year: int, indicator: str
) -> go.Figure:
    purpose = PURPOSE_LABELS[indicator]
    frame = metric(
        data,
        indicator=indicator,
        unit="PC_ENT_AI_TANY",
        source=SECTOR_SOURCE,
        geo=EU,
        size="GE10",
        sector=HIGH_LEVEL_SECTORS,
        year=year,
    )
    frame["sector"] = frame["nace_r2"].map(SECTOR_SHORT)
    frame = frame.sort_values("value")
    best = frame.iloc[-1]

    fig = go.Figure(
        go.Bar(
            x=frame["value"],
            y=frame["sector"],
            orientation="h",
            marker_color=[
                BLUE if code == best["nace_r2"] else LIGHT
                for code in frame["nace_r2"]
            ],
            text=[f"{value:.0f}%" for value in frame["value"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:.1f}% of AI adopters<extra></extra>",
        )
    )
    fig.update_xaxes(
        title="Share of AI-adopting enterprises",
        ticksuffix="%",
        range=[0, max(75, frame["value"].max() + 10)],
    )
    fig.update_yaxes(title=None)
    return apply_layout(
        fig,
        title=f"{best['sector']} leads AI use for {purpose.lower()}",
        subtitle=f"Selected business purpose by economic activity, {year}",
        height=520,
        margin={"l": 175, "r": 45, "t": 105, "b": 70},
    )


data = get_data()
country_lookup = (
    data[data["geo"].isin(EU27_CODES)][["geo", "geo_label"]]
    .drop_duplicates()
    .sort_values("geo_label")
)
country_options = dict(
    zip(country_lookup["geo_label"], country_lookup["geo"])
)

st.sidebar.title("Explore the story")
selected_year = st.sidebar.select_slider(
    "Year", options=[2023, 2024, 2025], value=2025
)
selected_country_name = st.sidebar.selectbox(
    "Focus country",
    options=list(country_options),
    index=list(country_options).index("Germany"),
)
selected_country = country_options[selected_country_name]
st.sidebar.markdown(
    """
    <div class="small-note">
    Filters update the exploratory charts. The main story figures remain fixed
    to protect their explanatory takeaway.
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Europe's AI Adoption Gap")
st.subheader(
    "Who is pulling ahead, where smaller firms fall behind, and what stops businesses from adopting AI?"
)
st.caption("Official Eurostat enterprise survey data · 27 EU countries · 2023–2025")

eu_2025 = metric(
    data,
    indicator="E_AI_TANY",
    unit="PC_ENT",
    geo=EU,
    size="GE10",
    sector=ALL_ACTIVITIES,
    year=2025,
)["value"].iloc[0]
eu_2023 = metric(
    data,
    indicator="E_AI_TANY",
    unit="PC_ENT",
    geo=EU,
    size="GE10",
    sector=ALL_ACTIVITIES,
    year=2023,
)["value"].iloc[0]
country_2025 = metric(
    data,
    indicator="E_AI_TANY",
    unit="PC_ENT",
    geo=EU27_CODES,
    size="GE10",
    sector=ALL_ACTIVITIES,
    year=2025,
)
leader = country_2025.loc[country_2025["value"].idxmax()]
small_2025 = metric(
    data,
    indicator="E_AI_TANY",
    unit="PC_ENT",
    geo=EU,
    size="10-49",
    sector=ALL_ACTIVITIES,
    year=2025,
)["value"].iloc[0]
large_2025 = metric(
    data,
    indicator="E_AI_TANY",
    unit="PC_ENT",
    geo=EU,
    size="GE250",
    sector=ALL_ACTIVITIES,
    year=2025,
)["value"].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "EU firms using AI",
    f"{format_1dp(eu_2025)}%",
    f"+{format_1dp(eu_2025 - eu_2023)} pp vs 2023",
)
col2.metric(
    "2025 leader",
    leader["geo_label"],
    f"{format_1dp(leader['value'])}%",
)
col3.metric(
    "Large-firm adoption",
    f"{format_1dp(large_2025)}%",
    "EU, 2025",
)
col4.metric(
    "Large-small gap",
    f"{format_1dp(large_2025 - small_2025)} pp",
    "EU, 2025",
)

overview_tab, size_tab, sector_tab, barrier_tab, about_tab = st.tabs(
    ["Overview", "Firm-size divide", "Sectors & use cases", "Barriers", "About"]
)

with overview_tab:
    st.markdown(
        """
        <div class="story-note"><b>Main finding:</b> AI adoption accelerated
        sharply, but the gains are uneven. Country, firm size, and digital
        maturity still determine who benefits first.</div>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_01_eu_acceleration(data), use_container_width=True)
    st.plotly_chart(
        country_ranking(data, selected_year, selected_country),
        use_container_width=True,
    )

with size_tab:
    st.plotly_chart(
        country_size_profile(data, selected_country), use_container_width=True
    )
    st.plotly_chart(fig_04_size_gap(data), use_container_width=True)

with sector_tab:
    st.plotly_chart(fig_07_sector_growth(data), use_container_width=True)
    left, right = st.columns([1, 1])
    with left:
        purpose_name = st.selectbox(
            "Business purpose",
            options=list(PURPOSE_LABELS.values()),
            index=0,
        )
    with right:
        purpose_year = st.selectbox(
            "Purpose year", options=[2024, 2025], index=1
        )
    purpose_code = next(
        code for code, label in PURPOSE_LABELS.items() if label == purpose_name
    )
    st.plotly_chart(
        sector_purpose_ranking(data, purpose_year, purpose_code),
        use_container_width=True,
    )
    with st.expander("See the full sector-by-purpose matrix"):
        st.plotly_chart(
            fig_09_sector_purpose_heatmap(data), use_container_width=True
        )

with barrier_tab:
    st.plotly_chart(fig_10_interest_vs_adoption(data), use_container_width=True)
    st.plotly_chart(fig_11_barriers(data), use_container_width=True)

with about_tab:
    st.markdown(
        """
        ### What this dashboard measures

        The figures show percentages from Eurostat's annual survey on ICT usage
        and e-commerce in enterprises. The scope is enterprises with at least
        10 people employed, excluding agriculture, mining, and the financial
        sector unless a figure explicitly uses an economic-activity breakdown.

        ### Data sources

        - [Artificial intelligence by size class of enterprise — isoc_eb_ai](https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en)
        - [Artificial intelligence by NACE activity — isoc_eb_ain2](https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ain2/default/table?lang=en)
        - [Eurostat methodology and 2025 analysis](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises)

        ### Important limitations

        - This is aggregate survey data, not firm-level microdata.
        - The analysis describes associations and gaps; it does not prove that
          firm size, sector, or any barrier causes adoption.
        - Eurostat flags are retained in the processed dataset. Comparisons
          involving flagged observations should be interpreted cautiously.
        - "Share of AI adopters" and "share of all enterprises" use different
          denominators; each visual states which denominator it uses.
        """
    )
