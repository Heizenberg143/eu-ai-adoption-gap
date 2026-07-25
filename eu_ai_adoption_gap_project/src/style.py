"""Shared visual language for every Plotly figure."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

import plotly.graph_objects as go


INK = "#172033"
MUTED = "#8A94A6"
LIGHT = "#E8ECF2"
PAPER = "#FFFFFF"
PANEL = "#F6F8FB"

# Okabe-Ito inspired, color-vision-deficiency-safe accents.
BLUE = "#0072B2"
SKY = "#56B4E9"
ORANGE = "#E69F00"
VERMILLION = "#D55E00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
YELLOW = "#F0E442"

SIZE_COLORS = {
    "All firms (10+)": INK,
    "Small (10–49)": SKY,
    "Medium (50–249)": ORANGE,
    "Large (250+)": VERMILLION,
}

SOURCE_NOTE = "Source: Eurostat — isoc_eb_ai and isoc_eb_ain2"


def format_1dp(value: float) -> str:
    """Format survey percentages with conventional half-up rounding."""

    rounded = Decimal(str(float(value))).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
    return f"{rounded:.1f}"


def title_with_subtitle(title: str, subtitle: str) -> str:
    return f"{title}<br><sup>{subtitle}</sup>"


def apply_layout(
    fig: go.Figure,
    *,
    title: str,
    subtitle: str,
    height: int = 520,
    source_note: str = SOURCE_NOTE,
    legend: bool = False,
    margin: dict | None = None,
) -> go.Figure:
    fig.update_layout(
        title={
            "text": title_with_subtitle(title, subtitle),
            "x": 0.02,
            "xanchor": "left",
            "y": 0.97,
            "yanchor": "top",
            "font": {"size": 23, "color": INK},
        },
        height=height,
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font={"family": "Arial, sans-serif", "color": INK, "size": 13},
        showlegend=legend,
        hoverlabel={
            "bgcolor": PAPER,
            "font": {"color": INK, "family": "Arial, sans-serif"},
            "bordercolor": LIGHT,
        },
        margin=margin or {"l": 65, "r": 35, "t": 105, "b": 70},
        annotations=[
            *list(fig.layout.annotations or []),
            {
                "text": source_note,
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.13,
                "showarrow": False,
                "font": {"size": 10, "color": MUTED},
                "xanchor": "left",
            },
        ],
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=LIGHT,
        tickfont={"color": INK},
        title_font={"color": INK},
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        linecolor=LIGHT,
        tickfont={"color": INK},
        title_font={"color": INK},
    )
    return fig
