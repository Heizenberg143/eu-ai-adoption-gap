"""Publication-ready Plotly figures for the twelve analytical questions."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.data import (
    ALL_ACTIVITIES,
    COUNTRY_SOURCE,
    EU,
    EU27_CODES,
    HIGH_LEVEL_SECTORS,
    SECTOR_SHORT,
    SECTOR_SOURCE,
    SIZE_SHORT,
    assert_unique,
    metric,
)
from src.style import (
    BLUE,
    GREEN,
    INK,
    LIGHT,
    MUTED,
    ORANGE,
    PURPLE,
    SIZE_COLORS,
    SKY,
    VERMILLION,
    apply_layout,
)


TECH_LABELS = {
    "E_AI_TTM": "Text mining",
    "E_AI_TSR": "Speech recognition",
    "E_AI_TNLG": "Language / code generation",
    "E_AI_TIR": "Image recognition",
    "E_AI_TML": "Machine learning",
    "E_AI_TPA": "Workflow automation",
    "E_AI_TAR": "Autonomous machines",
    "E_AI_TPVSG": "Image / audio / video generation",
}

PURPOSE_LABELS = {
    "E_AI_PMS": "Marketing & sales",
    "E_AI_PPP": "Production",
    "E_AI_PBAM": "Administration & management",
    "E_AI_PLOG": "Logistics",
    "E_AI_PITS": "ICT security",
    "E_AI_PFIN": "Finance & controlling",
    "E_AI_PRDI": "R&D & innovation",
}

BARRIER_LABELS = {
    "E_AI_BLE": "Lack of expertise",
    "E_AI_BLEG": "Unclear legal consequences",
    "E_AI_BCDP": "Data protection concerns",
    "E_AI_BCST": "Costs too high",
    "E_AI_BDDT": "Poor data availability / quality",
    "E_AI_BINC": "Incompatible systems",
    "E_AI_BEC": "Ethical concerns",
    "E_AI_BNU": "Not useful for the business",
}


def _country_adoption(data: pd.DataFrame, year: int) -> pd.DataFrame:
    return assert_unique(
        metric(
            data,
            indicator="E_AI_TANY",
            unit="PC_ENT",
            geo=EU27_CODES,
            size="GE10",
            sector=ALL_ACTIVITIES,
            year=year,
        ),
        ["geo", "time"],
        f"country adoption {year}",
    )


def fig_01_eu_acceleration(data: pd.DataFrame) -> go.Figure:
    sizes = ["GE10", "10-49", "50-249", "GE250"]
    frame = assert_unique(
        metric(
            data,
            indicator="E_AI_TANY",
            unit="PC_ENT",
            geo=EU,
            size=sizes,
            sector=ALL_ACTIVITIES,
            year=[2023, 2024, 2025],
        ),
        ["size_emp", "time"],
        "EU adoption trend",
    )
    frame["size_short"] = frame["size_emp"].map(SIZE_SHORT)

    small = frame.query("size_emp == '10-49' and time == 2025")["value"].iloc[0]
    large = frame.query("size_emp == 'GE250' and time == 2025")["value"].iloc[0]
    gap = large - small

    fig = go.Figure()
    for size in sizes:
        part = frame[frame["size_emp"].eq(size)].sort_values("time")
        label = SIZE_SHORT[size]
        fig.add_trace(
            go.Scatter(
                x=part["time"],
                y=part["value"],
                mode="lines+markers+text",
                name=label,
                text=[
                    "",
                    "",
                    f"<b>{label}</b>  {part['value'].iloc[-1]:.1f}%",
                ],
                textposition="middle right",
                cliponaxis=False,
                line={"width": 3, "color": SIZE_COLORS[label]},
                marker={
                    "size": 9,
                    "color": SIZE_COLORS[label],
                    "line": {"color": "white", "width": 1},
                },
                hovertemplate=f"{label}<br>%{{x}}: %{{y:.1f}}%<extra></extra>",
            )
        )
    fig.update_xaxes(
        tickmode="array",
        tickvals=[2023, 2024, 2025],
        range=[2022.85, 2025.55],
        title=None,
    )
    fig.update_yaxes(range=[0, 65], ticksuffix="%", title="Share of enterprises")
    return apply_layout(
        fig,
        title=f"AI adoption surged, but large firms still lead small firms by {gap:.0f} points",
        subtitle="Share of EU enterprises using at least one AI technology, by firm size",
        legend=False,
    )


def fig_02_country_divergence(data: pd.DataFrame) -> go.Figure:
    start = _country_adoption(data, 2023)[["geo", "geo_label", "value"]].rename(
        columns={"value": "value_2023"}
    )
    end = _country_adoption(data, 2025)[["geo", "value"]].rename(
        columns={"value": "value_2025"}
    )
    frame = start.merge(end, on="geo", validate="one_to_one")
    frame["change"] = frame["value_2025"] - frame["value_2023"]
    frame = frame.sort_values("value_2025")

    fig = go.Figure()
    for row in frame.itertuples():
        fig.add_shape(
            type="line",
            x0=row.value_2023,
            x1=row.value_2025,
            y0=row.geo_label,
            y1=row.geo_label,
            line={"color": LIGHT, "width": 4},
            layer="below",
        )
    fig.add_trace(
        go.Scatter(
            x=frame["value_2023"],
            y=frame["geo_label"],
            mode="markers",
            name="2023",
            marker={"size": 7, "color": MUTED},
            hovertemplate="<b>%{y}</b><br>2023: %{x:.1f}%<extra></extra>",
        )
    )
    end_colors = frame["geo"].map(
        lambda code: VERMILLION if code == "DE" else BLUE
    )
    fig.add_trace(
        go.Scatter(
            x=frame["value_2025"],
            y=frame["geo_label"],
            mode="markers",
            name="2025",
            marker={"size": 9, "color": end_colors},
            customdata=frame["change"],
            hovertemplate=(
                "<b>%{y}</b><br>2025: %{x:.1f}%"
                "<br>Change since 2023: +%{customdata:.1f} pp<extra></extra>"
            ),
        )
    )
    high = frame.iloc[-1]
    low = frame.iloc[0]
    spread = high["value_2025"] - low["value_2025"]
    fig.update_xaxes(title="Share of enterprises using AI", ticksuffix="%", range=[0, 46])
    fig.update_yaxes(title=None, tickfont={"size": 10})
    return apply_layout(
        fig,
        title=f"Rapid growth has not closed Europe’s {spread:.0f}-point country adoption divide",
        subtitle="AI use by country, 2023 versus 2025; Germany highlighted in orange",
        height=700,
        legend=True,
        margin={"l": 115, "r": 35, "t": 105, "b": 70},
    )


def fig_03_country_acceleration(data: pd.DataFrame) -> go.Figure:
    start = _country_adoption(data, 2024)[
        ["geo", "geo_label", "iso_alpha", "value"]
    ].rename(columns={"value": "adoption_2024"})
    end = _country_adoption(data, 2025)[["geo", "value"]].rename(
        columns={"value": "adoption_2025"}
    )
    frame = start.merge(end, on="geo", validate="one_to_one")
    frame["change"] = frame["adoption_2025"] - frame["adoption_2024"]
    x_median = frame["adoption_2024"].median()
    y_median = frame["change"].median()

    leader = frame.loc[frame["change"].idxmax()]
    highlight_codes = ["DK", "FI", "LT", "DE", "RO"]
    colors = frame["geo"].map(
        lambda code: VERMILLION if code == "DE" else BLUE if code in highlight_codes else MUTED
    )
    sizes = frame["geo"].map(lambda code: 12 if code in highlight_codes else 8)

    fig = go.Figure(
        go.Scatter(
            x=frame["adoption_2024"],
            y=frame["change"],
            mode="markers+text",
            text=[
                row.geo_label if row.geo in highlight_codes else ""
                for row in frame.itertuples()
            ],
            textposition=[
                "top center" if row.geo != "DE" else "bottom center"
                for row in frame.itertuples()
            ],
            marker={
                "size": sizes,
                "color": colors,
                "opacity": 0.9,
                "line": {"color": "white", "width": 1},
            },
            customdata=np.column_stack(
                [frame["geo_label"], frame["adoption_2025"]]
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "2024: %{x:.1f}%<br>2025: %{customdata[1]:.1f}%<br>"
                "Change: +%{y:.1f} pp<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=x_median, line_dash="dot", line_color=LIGHT)
    fig.add_hline(y=y_median, line_dash="dot", line_color=LIGHT)
    fig.update_xaxes(title="AI adoption in 2024", ticksuffix="%")
    fig.update_yaxes(title="Increase from 2024 to 2025", ticksuffix=" pp", rangemode="tozero")
    return apply_layout(
        fig,
        title=f"{leader['geo_label']} accelerated fastest, adding {leader['change']:.1f} points in one year",
        subtitle="Starting position versus one-year change; Germany highlighted in orange",
    )


def fig_04_size_gap(data: pd.DataFrame) -> go.Figure:
    small = metric(
        data,
        indicator="E_AI_TANY",
        unit="PC_ENT",
        geo=EU27_CODES,
        size="10-49",
        sector=ALL_ACTIVITIES,
        year=2025,
    )[["geo", "geo_label", "value"]].rename(columns={"value": "small"})
    large = metric(
        data,
        indicator="E_AI_TANY",
        unit="PC_ENT",
        geo=EU27_CODES,
        size="GE250",
        sector=ALL_ACTIVITIES,
        year=2025,
    )[["geo", "value"]].rename(columns={"value": "large"})
    frame = small.merge(large, on="geo", validate="one_to_one")
    frame["gap"] = frame["large"] - frame["small"]
    frame = frame.nlargest(12, "gap").sort_values("gap")

    fig = go.Figure()
    for row in frame.itertuples():
        fig.add_shape(
            type="line",
            x0=row.small,
            x1=row.large,
            y0=row.geo_label,
            y1=row.geo_label,
            line={"color": LIGHT, "width": 5},
            layer="below",
        )
    fig.add_trace(
        go.Scatter(
            x=frame["small"],
            y=frame["geo_label"],
            mode="markers",
            name="Small firms",
            marker={"size": 10, "color": SKY},
            hovertemplate="<b>%{y}</b><br>Small firms: %{x:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=frame["large"],
            y=frame["geo_label"],
            mode="markers+text",
            name="Large firms",
            text=[f"{value:.0f} pp" for value in frame["gap"]],
            textposition="middle right",
            cliponaxis=False,
            marker={"size": 11, "color": VERMILLION},
            customdata=frame["gap"],
            hovertemplate=(
                "<b>%{y}</b><br>Large firms: %{x:.1f}%"
                "<br>Large–small gap: %{customdata:.1f} pp<extra></extra>"
            ),
        )
    )
    fig.update_xaxes(title="Share using AI", ticksuffix="%", range=[0, 90])
    fig.update_yaxes(title=None)
    top = frame.iloc[-1]
    return apply_layout(
        fig,
        title=f"{top['geo_label']} has Europe’s widest large–small AI adoption gap",
        subtitle="Twelve largest percentage-point gaps between large and small enterprises, 2025",
        legend=True,
        margin={"l": 145, "r": 70, "t": 105, "b": 70},
    )


def fig_05_maturity(data: pd.DataFrame) -> go.Figure:
    indicators = ["E_AI_TANY", "E_AI_TGE2", "E_AI_TGE3"]
    labels = {
        "E_AI_TANY": "At least 1 technology",
        "E_AI_TGE2": "At least 2",
        "E_AI_TGE3": "At least 3",
    }
    sizes = ["10-49", "50-249", "GE250"]
    parts = [
        metric(
            data,
            indicator=indicator,
            unit="PC_ENT",
            geo=EU,
            size=sizes,
            sector=ALL_ACTIVITIES,
            year=2025,
        ).assign(maturity=labels[indicator])
        for indicator in indicators
    ]
    frame = pd.concat(parts, ignore_index=True)
    frame["size_short"] = frame["size_emp"].map(SIZE_SHORT)

    fig = go.Figure()
    for size in sizes:
        part = frame[frame["size_emp"].eq(size)].copy()
        part["order"] = part["indic_is"].map(
            {"E_AI_TANY": 1, "E_AI_TGE2": 2, "E_AI_TGE3": 3}
        )
        part = part.sort_values("order")
        label = SIZE_SHORT[size]
        fig.add_trace(
            go.Scatter(
                x=part["maturity"],
                y=part["value"],
                mode="lines+markers+text",
                name=label,
                text=[f"{v:.1f}%" for v in part["value"]],
                textposition="top center",
                line={"width": 3, "color": SIZE_COLORS[label]},
                marker={"size": 10, "color": SIZE_COLORS[label]},
                hovertemplate=f"{label}<br>%{{x}}: %{{y:.1f}}%<extra></extra>",
            )
        )
    eu_three = metric(
        data,
        indicator="E_AI_TGE3",
        unit="PC_ENT",
        geo=EU,
        size="GE10",
        sector=ALL_ACTIVITIES,
        year=2025,
    )["value"].iloc[0]
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Share of all enterprises", ticksuffix="%", range=[0, 65])
    return apply_layout(
        fig,
        title=f"AI breadth remains limited: only {eu_three:.1f}% of EU firms use three or more technologies",
        subtitle="Technology adoption maturity by firm size, 2025",
        legend=True,
    )


def fig_06_technology_mix(data: pd.DataFrame) -> go.Figure:
    techs = list(TECH_LABELS)
    sizes = ["10-49", "GE250"]
    rows = []
    for size in sizes:
        adoption = metric(
            data,
            indicator="E_AI_TANY",
            unit="PC_ENT",
            geo=EU,
            size=size,
            sector=ALL_ACTIVITIES,
            year=2025,
        )["value"].iloc[0]
        for indicator in techs:
            part = metric(
                data,
                indicator=indicator,
                unit="PC_ENT",
                geo=EU,
                size=size,
                sector=ALL_ACTIVITIES,
                year=2025,
            )
            if part.empty:
                continue
            rows.append(
                {
                    "size_emp": size,
                    "technology": TECH_LABELS[indicator],
                    "share_of_adopters": part["value"].iloc[0] / adoption * 100,
                }
            )
    frame = pd.DataFrame(rows)
    order = (
        frame.groupby("technology")["share_of_adopters"]
        .mean()
        .sort_values()
        .index.tolist()
    )

    fig = go.Figure()
    for technology in order:
        part = frame[frame["technology"].eq(technology)].set_index("size_emp")
        if set(sizes).issubset(part.index):
            fig.add_shape(
                type="line",
                x0=part.loc["10-49", "share_of_adopters"],
                x1=part.loc["GE250", "share_of_adopters"],
                y0=technology,
                y1=technology,
                line={"color": LIGHT, "width": 5},
                layer="below",
            )
    for size, color, label in [
        ("10-49", SKY, "Small adopters"),
        ("GE250", VERMILLION, "Large adopters"),
    ]:
        part = frame[frame["size_emp"].eq(size)].set_index("technology").loc[order].reset_index()
        fig.add_trace(
            go.Scatter(
                x=part["share_of_adopters"],
                y=part["technology"],
                mode="markers",
                name=label,
                marker={"size": 11, "color": color},
                hovertemplate=f"<b>%{{y}}</b><br>{label}: %{{x:.0f}}%<extra></extra>",
            )
        )
    fig.update_xaxes(title="Technology users as a share of AI-adopting firms", ticksuffix="%")
    fig.update_yaxes(title=None)
    return apply_layout(
        fig,
        title="Large firms do not just adopt more AI — they build a broader technology stack",
        subtitle="Technology mix among AI adopters, small versus large EU enterprises, 2025",
        legend=True,
        margin={"l": 190, "r": 35, "t": 105, "b": 70},
    )


def fig_07_sector_growth(data: pd.DataFrame) -> go.Figure:
    frames = []
    for year in [2023, 2025]:
        part = metric(
            data,
            indicator="E_AI_TANY",
            unit="PC_ENT",
            source=SECTOR_SOURCE,
            geo=EU,
            size="GE10",
            sector=HIGH_LEVEL_SECTORS,
            year=year,
        )[["nace_r2", "value"]].rename(columns={"value": f"value_{year}"})
        frames.append(part)
    frame = frames[0].merge(frames[1], on="nace_r2", validate="one_to_one")
    frame["sector"] = frame["nace_r2"].map(SECTOR_SHORT)
    frame["change"] = frame["value_2025"] - frame["value_2023"]
    frame = frame.sort_values("value_2025")

    fig = go.Figure()
    for row in frame.itertuples():
        fig.add_shape(
            type="line",
            x0=row.value_2023,
            x1=row.value_2025,
            y0=row.sector,
            y1=row.sector,
            line={"color": LIGHT, "width": 5},
            layer="below",
        )
    fig.add_trace(
        go.Scatter(
            x=frame["value_2023"],
            y=frame["sector"],
            mode="markers",
            name="2023",
            marker={"size": 9, "color": MUTED},
            hovertemplate="<b>%{y}</b><br>2023: %{x:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=frame["value_2025"],
            y=frame["sector"],
            mode="markers+text",
            name="2025",
            text=[f"{value:.1f}%" for value in frame["value_2025"]],
            textposition="middle right",
            cliponaxis=False,
            marker={"size": 11, "color": BLUE},
            hovertemplate="<b>%{y}</b><br>2025: %{x:.1f}%<extra></extra>",
        )
    )
    leader = frame.iloc[-1]
    trailer = frame.iloc[0]
    fig.update_xaxes(title="Share of enterprises using AI", ticksuffix="%", range=[0, 70])
    fig.update_yaxes(title=None)
    return apply_layout(
        fig,
        title=f"{leader['sector']} reached {leader['value_2025']:.0f}% adoption; {trailer['sector']} remains near {trailer['value_2025']:.0f}%",
        subtitle="AI adoption by economic activity, 2023 versus 2025",
        legend=True,
        margin={"l": 175, "r": 55, "t": 105, "b": 70},
    )


def fig_08_purpose_growth(data: pd.DataFrame) -> go.Figure:
    indicators = list(PURPOSE_LABELS)
    frames = []
    for year in [2024, 2025]:
        parts = [
            metric(
                data,
                indicator=indicator,
                unit="PC_ENT_AI_TANY",
                geo=EU,
                size="GE10",
                sector=ALL_ACTIVITIES,
                year=year,
            ).assign(purpose=PURPOSE_LABELS[indicator])
            for indicator in indicators
        ]
        part = pd.concat(parts, ignore_index=True)[["indic_is", "purpose", "value"]]
        frames.append(part.rename(columns={"value": f"value_{year}"}))
    frame = frames[0].merge(
        frames[1], on=["indic_is", "purpose"], validate="one_to_one"
    )
    frame["change"] = frame["value_2025"] - frame["value_2024"]
    frame = frame.sort_values("value_2025")

    fig = go.Figure()
    for row in frame.itertuples():
        fig.add_shape(
            type="line",
            x0=row.value_2024,
            x1=row.value_2025,
            y0=row.purpose,
            y1=row.purpose,
            line={"color": LIGHT, "width": 5},
            layer="below",
        )
    fig.add_trace(
        go.Scatter(
            x=frame["value_2024"],
            y=frame["purpose"],
            mode="markers",
            name="2024",
            marker={"size": 9, "color": MUTED},
            hovertemplate="<b>%{y}</b><br>2024: %{x:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=frame["value_2025"],
            y=frame["purpose"],
            mode="markers+text",
            name="2025",
            text=[f"{value:.0f}%" for value in frame["value_2025"]],
            textposition="middle right",
            cliponaxis=False,
            marker={"size": 11, "color": GREEN},
            hovertemplate="<b>%{y}</b><br>2025: %{x:.1f}%<extra></extra>",
        )
    )
    fastest = frame.loc[frame["change"].idxmax()]
    fig.update_xaxes(
        title="Share of AI-adopting enterprises using AI for this purpose",
        ticksuffix="%",
        range=[0, max(frame["value_2025"].max() + 10, 60)],
    )
    fig.update_yaxes(title=None)
    return apply_layout(
        fig,
        title=f"{fastest['purpose']} recorded the largest one-year gain among AI use cases",
        subtitle="Business purposes among EU enterprises already using AI, 2024 versus 2025",
        legend=True,
        margin={"l": 190, "r": 55, "t": 105, "b": 70},
    )


def fig_09_sector_purpose_heatmap(data: pd.DataFrame) -> go.Figure:
    rows = []
    for indicator, purpose in PURPOSE_LABELS.items():
        part = metric(
            data,
            indicator=indicator,
            unit="PC_ENT_AI_TANY",
            source=SECTOR_SOURCE,
            geo=EU,
            size="GE10",
            sector=HIGH_LEVEL_SECTORS,
            year=2025,
        )
        part = part.assign(purpose=purpose)
        rows.append(part[["nace_r2", "purpose", "value"]])
    frame = pd.concat(rows, ignore_index=True)
    frame["sector"] = frame["nace_r2"].map(SECTOR_SHORT)
    pivot = frame.pivot(index="sector", columns="purpose", values="value")
    pivot = pivot.loc[[SECTOR_SHORT[code] for code in HIGH_LEVEL_SECTORS]]
    pivot = pivot[list(PURPOSE_LABELS.values())]

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=[
                [0.0, "#F3F5F8"],
                [0.4, "#B7D8E9"],
                [0.7, "#4A9AC4"],
                [1.0, BLUE],
            ],
            zmin=0,
            zmax=max(70, float(np.nanmax(pivot.values))),
            text=np.where(
                np.isnan(pivot.values),
                "",
                np.vectorize(lambda value: f"{value:.0f}%")(pivot.values),
            ),
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar={
                "title": "%",
                "thickness": 12,
                "outlinewidth": 0,
            },
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>",
        )
    )
    return apply_layout(
        fig,
        title="There is no universal AI playbook: each sector concentrates on different use cases",
        subtitle="Purpose mix among AI-adopting enterprises, by economic activity, 2025",
        height=610,
        margin={"l": 185, "r": 50, "t": 105, "b": 125},
    )


def fig_10_interest_vs_adoption(data: pd.DataFrame) -> go.Figure:
    adoption = metric(
        data,
        indicator="E_AI_TANY",
        unit="PC_ENT",
        source=SECTOR_SOURCE,
        geo=EU,
        size="GE10",
        sector=HIGH_LEVEL_SECTORS,
        year=2025,
    )[["nace_r2", "value"]].rename(columns={"value": "adoption"})
    considered = metric(
        data,
        indicator="E_AI_EC",
        unit="PC_ENT_AI_TX",
        source=SECTOR_SOURCE,
        geo=EU,
        size="GE10",
        sector=HIGH_LEVEL_SECTORS,
        year=2025,
    )[["nace_r2", "value"]].rename(columns={"value": "considered"})
    frame = adoption.merge(considered, on="nace_r2", validate="one_to_one")
    frame["sector"] = frame["nace_r2"].map(SECTOR_SHORT)

    x_median = frame["adoption"].median()
    y_median = frame["considered"].median()
    colors = frame["nace_r2"].map(
        lambda code: BLUE if code in ["J", "M"] else VERMILLION if code == "F" else MUTED
    )
    direct_labels = frame.apply(
        lambda row: row["sector"]
        if row["nace_r2"] in ["J", "M", "F", "D", "L"]
        else "",
        axis=1,
    )
    fig = go.Figure(
        go.Scatter(
            x=frame["adoption"],
            y=frame["considered"],
            mode="markers+text",
            text=direct_labels,
            textposition="top center",
            marker={
                "size": 13,
                "color": colors,
                "line": {"color": "white", "width": 1},
            },
            customdata=frame["sector"],
            hovertemplate=(
                "<b>%{customdata}</b><br>Already using AI: %{x:.1f}%"
                "<br>Non-users that considered AI: %{y:.1f}%<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=x_median, line_dash="dot", line_color=LIGHT)
    fig.add_hline(y=y_median, line_dash="dot", line_color=LIGHT)
    fig.update_xaxes(title="Enterprises already using AI", ticksuffix="%")
    fig.update_yaxes(title="Non-users that considered AI", ticksuffix="%")
    return apply_layout(
        fig,
        title="AI interest is strongest where adoption is already high — the sector gap may persist",
        subtitle="Current adoption versus stated consideration among non-adopters, 2025",
        height=570,
    )


def fig_11_barriers(data: pd.DataFrame) -> go.Figure:
    sizes = ["10-49", "50-249", "GE250"]
    rows = []
    for indicator, barrier in BARRIER_LABELS.items():
        part = metric(
            data,
            indicator=indicator,
            unit="PC_ENT_AI_EC",
            geo=EU,
            size=sizes,
            sector=ALL_ACTIVITIES,
            year=2025,
        ).assign(barrier=barrier)
        rows.append(part)
    frame = pd.concat(rows, ignore_index=True)
    frame["size_short"] = frame["size_emp"].map(SIZE_SHORT)
    order = (
        frame.groupby("barrier")["value"].mean().sort_values().index.tolist()
    )

    fig = go.Figure()
    for size in sizes:
        label = SIZE_SHORT[size]
        part = (
            frame[frame["size_emp"].eq(size)]
            .set_index("barrier")
            .loc[order]
            .reset_index()
        )
        fig.add_trace(
            go.Scatter(
                x=part["value"],
                y=part["barrier"],
                mode="markers",
                name=label,
                marker={
                    "size": 10,
                    "color": SIZE_COLORS[label],
                    "opacity": 0.9,
                },
                hovertemplate=f"<b>%{{y}}</b><br>{label}: %{{x:.1f}}%<extra></extra>",
            )
        )
    expertise = frame[frame["barrier"].eq("Lack of expertise")]["value"].mean()
    fig.update_xaxes(
        title="Share of firms that considered AI but did not adopt it",
        ticksuffix="%",
        range=[0, 80],
    )
    fig.update_yaxes(title=None)
    return apply_layout(
        fig,
        title=f"Skills—not cost—are the dominant AI blocker across every firm size",
        subtitle=f"Lack of expertise is cited by roughly {expertise:.0f}% of firms that considered AI, 2025",
        legend=True,
        margin={"l": 205, "r": 35, "t": 105, "b": 70},
    )


def fig_12_digital_foundations(data: pd.DataFrame) -> go.Figure:
    sizes = ["10-49", "50-249", "GE250"]
    labels = {
        "E_AI_DA": "AI + data analytics",
        "E_AI_CC": "AI + cloud services",
    }
    rows = []
    for size in sizes:
        adoption = metric(
            data,
            indicator="E_AI_TANY",
            unit="PC_ENT",
            geo=EU,
            size=size,
            sector=ALL_ACTIVITIES,
            year=2025,
        )["value"].iloc[0]
        for indicator, label in labels.items():
            joint = metric(
                data,
                indicator=indicator,
                unit="PC_ENT",
                geo=EU,
                size=size,
                sector=ALL_ACTIVITIES,
                year=2025,
            )
            if joint.empty:
                continue
            rows.append(
                {
                    "size_emp": size,
                    "foundation": label,
                    "share": joint["value"].iloc[0] / adoption * 100,
                }
            )
    frame = pd.DataFrame(rows)
    frame["size_short"] = frame["size_emp"].map(SIZE_SHORT)

    fig = go.Figure()
    for foundation, color in [
        ("AI + data analytics", BLUE),
        ("AI + cloud services", ORANGE),
    ]:
        part = frame[frame["foundation"].eq(foundation)]
        fig.add_trace(
            go.Bar(
                x=part["size_short"],
                y=part["share"],
                name=foundation,
                marker_color=color,
                text=[f"{value:.0f}%" for value in part["share"]],
                textposition="outside",
                cliponaxis=False,
                hovertemplate=f"{foundation}<br>%{{x}}: %{{y:.1f}}%<extra></extra>",
            )
        )
    fig.update_layout(barmode="group", bargap=0.35)
    fig.update_xaxes(title=None)
    fig.update_yaxes(
        title="Share of AI adopters also using the foundation",
        ticksuffix="%",
        range=[0, 110],
    )
    return apply_layout(
        fig,
        title="AI adoption is rarely isolated: analytics and cloud are complementary foundations",
        subtitle="Joint use as a share of AI-adopting EU enterprises, 2025",
        legend=True,
    )


FIGURE_BUILDERS = [
    fig_01_eu_acceleration,
    fig_02_country_divergence,
    fig_03_country_acceleration,
    fig_04_size_gap,
    fig_05_maturity,
    fig_06_technology_mix,
    fig_07_sector_growth,
    fig_08_purpose_growth,
    fig_09_sector_purpose_heatmap,
    fig_10_interest_vs_adoption,
    fig_11_barriers,
    fig_12_digital_foundations,
]
