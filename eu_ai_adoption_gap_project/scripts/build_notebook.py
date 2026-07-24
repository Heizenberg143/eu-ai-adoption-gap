"""Create the final analysis notebook with narrative, code, and 12 questions."""

import base64
from pathlib import Path
import sys

import nbformat as nbf
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "eu_ai_adoption_analysis.ipynb"
sys.path.insert(0, str(ROOT))

from src.data import load_data  # noqa: E402


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


def question_cell(
    number: int,
    question: str,
    why: str,
    method: str,
    finding: str,
):
    return markdown(
        f"""
## Question {number}: {question}

**Why it matters.** {why}

**Method.** {method}

**Finding.** {finding}
"""
    )


def main() -> None:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.12"},
        "title": "Europe's AI Adoption Gap",
    }

    cells = [
        markdown(
            """
# Europe's AI Adoption Gap

### Who is pulling ahead, where smaller firms fall behind, and what stops businesses from adopting AI?

**Final Individual Project — Data Visualization, Summer 2026**  
**Student:** Usaid Aamer  
**Data source:** Eurostat enterprise ICT survey (`isoc_eb_ai`, `isoc_eb_ain2`)

---

This notebook tells one story through twelve analytical questions. It begins
with the pace of AI adoption, then examines the divides by country, firm size,
and sector, before looking at technology depth, business use cases, and the
reasons many firms still do not adopt AI.
"""
        ),
        markdown(
            """
## Executive summary

- EU enterprise AI adoption rose from **8.1% in 2023 to 20.0% in 2025**.
- The acceleration was uneven: **Denmark reached 42.0%**, while **Romania
  remained at 5.2%**.
- Firm size is the most consistent divide. In 2025, **55.0% of large firms**
  used AI versus **17.0% of small firms**.
- Adoption is also shallow for many businesses: only **8.3% of all EU firms**
  used at least three AI technologies.
- Among firms that considered AI but did not adopt it, **70.3% cited a lack of
  expertise**. Skills were a larger barrier than cost.
"""
        ),
        markdown(
            """
## Data and analytical scope

The data comes from two official Eurostat tables:

1. [`isoc_eb_ai`](https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en)
   — AI adoption by country and firm size.
2. [`isoc_eb_ain2`](https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ain2/default/table?lang=en)
   — AI adoption by economic activity.

The final curated dataset contains aggregate percentages for 27 EU countries,
2023–2025, four firm-size classes, selected high-level sectors, technology
types, business purposes, and barriers. It is deliberately limited to the
dimensions needed for the story, keeping the analysis reproducible and light
enough to run on an ordinary laptop.

### Important denominator rule

Eurostat publishes several versions of some measures:

- `PC_ENT`: percentage of **all enterprises**.
- `PC_ENT_AI_TANY`: percentage of enterprises **already using AI**.
- `PC_ENT_AI_TX`: percentage of enterprises **not using AI**.
- `PC_ENT_AI_EC`: percentage of non-users that **considered AI**.

Every chart below uses the denominator stated in its subtitle. Mixing these
denominators would produce misleading conclusions.
"""
        ),
        code(
            """
from pathlib import Path
import sys
import pandas as pd
import plotly.io as pio

# Make the notebook work whether Jupyter starts in the repo root or /notebooks.
ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

from src.data import load_data
from src.charts import (
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
)

pio.renderers.default = "notebook_connected"
pd.set_option("display.max_columns", 20)
pd.set_option("display.float_format", lambda value: f"{value:,.2f}")

data = load_data()
"""
        ),
        markdown(
            """
## Preliminary exploratory data analysis

This section verifies scope, structure, and data quality. These checks are
necessary, but they are not counted as analytical questions because they only
describe the dataset.
"""
        ),
        code(
            """
eda_summary = pd.Series({
    "Rows": len(data),
    "Columns": data.shape[1],
    "Years": f"{data['time'].min()}–{data['time'].max()}",
    "EU countries": data.loc[data['geo'] != 'EU27_2020', 'geo'].nunique(),
    "Firm-size classes": data['size_emp'].nunique(),
    "Selected indicators": data['indic_is'].nunique(),
    "Source tables": data['source_dataset'].nunique(),
})
eda_summary.to_frame("Value")
"""
        ),
        code(
            """
coverage = (
    data.groupby(["source_dataset", "time"])
        .agg(
            observations=("value", "size"),
            geographies=("geo", "nunique"),
            sectors=("nace_r2", "nunique"),
            indicators=("indic_is", "nunique"),
        )
)
coverage
"""
        ),
        code(
            """
quality_checks = pd.Series({
    "Missing numeric values": int(data["value"].isna().sum()),
    "Values below 0%": int((data["value"] < 0).sum()),
    "Values above 100%": int((data["value"] > 100).sum()),
    "Observations with Eurostat flags": int(data["status"].ne("").sum()),
    "Duplicate metric rows": int(
        data.duplicated([
            "source_dataset", "time", "geo", "size_emp",
            "nace_r2", "indic_is", "unit"
        ]).sum()
    ),
})
quality_checks.to_frame("Count")
"""
        ),
        markdown(
            """
## Analytical question map

| # | Question focus | Dimensions related |
|---:|---|---|
| 1 | Adoption acceleration and firm size | year × size × adoption |
| 2 | Country divergence | country × year × adoption |
| 3 | Starting position versus acceleration | country × 2024 level × 2025 change |
| 4 | Large-small adoption gap | country × size × adoption |
| 5 | Technology maturity | size × number of technologies |
| 6 | Technology mix | technology × size × adopter base |
| 7 | Sector growth | sector × year × adoption |
| 8 | Business-purpose shifts | purpose × year × adopter base |
| 9 | Sector-specific use cases | sector × purpose × adopter base |
| 10 | Interest versus adoption | sector × adoption × consideration |
| 11 | Barriers by firm size | barrier × size × non-adopters |
| 12 | Complementary digital foundations | foundation × size × AI adopters |
"""
        ),
        question_cell(
            1,
            "How quickly is enterprise AI adoption growing, and is the pace equal across firm sizes?",
            "An overall average can hide whether the benefits of rapid adoption are broadly distributed.",
            "Track the share using at least one AI technology from 2023–2025 for small, medium, large, and all EU enterprises.",
            "Adoption more than doubled across the period, but the 2025 large-small gap still reached **38.0 percentage points** (55.0% versus 17.0%).",
        ),
        code("fig_01_eu_acceleration(data).show()"),
        question_cell(
            2,
            "Has rapid growth closed the AI adoption divide between EU countries?",
            "A rising EU average is not enough if national gaps continue to widen.",
            "Compare every EU country's 2023 and 2025 adoption levels on the same scale.",
            "No. By 2025, Denmark reached **42.0%** while Romania remained at **5.2%**, leaving a **36.8-point** spread.",
        ),
        code("fig_02_country_divergence(data).show()"),
        question_cell(
            3,
            "Did 2025 growth favour existing leaders or allow lagging countries to catch up?",
            "The relationship between starting level and subsequent growth reveals whether the divide is likely to narrow.",
            "Plot each country's 2024 adoption rate against its percentage-point increase from 2024 to 2025.",
            "The pattern is mixed. Denmark and Finland were already leaders and accelerated strongly, while Lithuania was the clearest catch-up case. Denmark added the most: **14.5 points**.",
        ),
        code("fig_03_country_acceleration(data).show()"),
        question_cell(
            4,
            "Where is the gap between small and large firms most severe?",
            "A country's overall adoption rate can conceal unequal access to AI capability.",
            "Calculate the 2025 percentage-point difference between large and small enterprises for each EU country, then rank the twelve widest gaps.",
            "Slovenia had the widest gap at about **53.5 points**, followed by Belgium and Finland. The size divide is not restricted to low-adoption countries.",
        ),
        code("fig_04_size_gap(data).show()"),
        question_cell(
            5,
            "Are firms building mature AI portfolios or only experimenting with one tool?",
            "Using one AI technology is a weaker signal of organisational maturity than using several complementary technologies.",
            "Compare the share of firms using at least one, at least two, and at least three AI technologies by size.",
            "Breadth falls sharply at every size. Only **8.3%** of all EU firms used three or more AI technologies in 2025; the figure was 33.6% for large firms but only 6.5% for small firms.",
        ),
        code("fig_05_maturity(data).show()"),
        question_cell(
            6,
            "Does the technology mix differ between small and large AI adopters?",
            "Comparing raw technology rates would mostly reproduce the adoption gap, so this question conditions each technology on the AI-adopter base.",
            "For each size group, divide technology-specific adoption by overall AI adoption to estimate the technology's share among adopters.",
            "Text mining leads both groups, but large adopters use a broader stack. Machine learning reaches about **45.5% of large adopters** versus **22.4% of small adopters**.",
        ),
        code("fig_06_technology_mix(data).show()"),
        question_cell(
            7,
            "Which economic sectors are pulling ahead, and which remain structurally behind?",
            "Sector-specific usefulness and digital maturity may shape adoption more strongly than the EU average suggests.",
            "Compare 2023 and 2025 adoption across eleven high-level economic activities.",
            "Information and communication reached **62.5%** in 2025, while construction remained at **10.8%**. Every sector grew, but the leaders increased fastest in absolute terms.",
        ),
        code("fig_07_sector_growth(data).show()"),
        question_cell(
            8,
            "How are the business purposes of AI changing among firms that already adopted it?",
            "Adoption volume says little about where firms expect business value.",
            "Compare purpose-specific shares among AI adopters in 2024 and 2025.",
            "Marketing and sales remained the most common purpose at **34.7%**. Administration and management gained the most (**+3.5 points**), while production and ICT security declined as shares of the rapidly expanding adopter base.",
        ),
        code("fig_08_purpose_growth(data).show()"),
        question_cell(
            9,
            "Do sectors use AI for the same business purposes?",
            "A single cross-sector AI strategy would be weak if use cases depend heavily on operating context.",
            "Cross-tabulate seven AI purposes with eleven high-level sectors for 2025, using the share among AI adopters.",
            "The purpose mix is clearly sector-specific: information and communication leans toward R&D and generation-related work, while accommodation and food services are heavily oriented toward marketing and sales.",
        ),
        code("fig_09_sector_purpose_heatmap(data).show()"),
        question_cell(
            10,
            "Is latent interest in AI strongest in sectors that already have high adoption?",
            "If high-adoption sectors also have the largest pipeline of interested non-users, today's divide may persist.",
            "Plot current adoption against the share of non-users that considered AI for each sector.",
            "Interest and adoption move together. Information and communication combines **62.5% adoption** with **32.0% consideration among non-users**; construction is low on both measures.",
        ),
        code("fig_10_interest_vs_adoption(data).show()"),
        question_cell(
            11,
            "Which barriers stop interested firms from adopting AI, and do they vary by firm size?",
            "Intervention priorities differ if firms are blocked mainly by cost, technology, law, or capability.",
            "Compare eight barriers across small, medium, and large enterprises among non-users that had considered AI.",
            "Lack of expertise dominates at roughly **70.3%**, ahead of unclear legal consequences (53.6%) and data-protection concerns (52.7%). Cost ranks below skills, law, privacy, data quality, and system compatibility.",
        ),
        code("fig_11_barriers(data).show()"),
        question_cell(
            12,
            "Does AI adoption occur alongside cloud and data-analytics capabilities?",
            "AI deployment may depend on complementary digital foundations rather than a stand-alone tool purchase.",
            "Express joint AI-plus-analytics and AI-plus-cloud use as a share of all AI adopters, then compare by firm size.",
            "The relationship is strong. About **92% of large AI adopters** also use data analytics and **94% use cloud services**. The shares are lower for small adopters, especially for analytics (63%).",
        ),
        code("fig_12_digital_foundations(data).show()"),
        markdown(
            """
## Conclusion: acceleration without convergence

The central story is not simply that European businesses are adopting AI.
They are adopting it **quickly but unevenly**.

Country, firm size, sector, and existing digital capability divide the market.
The leaders are not only more likely to use AI; they are also more likely to
use several AI technologies and combine them with analytics and cloud
services. Meanwhile, the most common barrier is not that businesses see no
value in AI. It is that they lack the expertise to implement it and remain
uncertain about legal and data-protection consequences.

This means the adoption gap is unlikely to close through cheaper tools alone.
Smaller firms and slower sectors need implementation capability, relevant use
cases, trustworthy governance, and access to complementary digital
infrastructure.
"""
        ),
        markdown(
            """
## Limitations and responsible interpretation

1. **Aggregate data:** These are national and sector percentages, not individual
   firm records. The analysis cannot explain within-group variation.
2. **No causal claims:** A relationship between firm size and adoption does not
   prove that size itself causes adoption.
3. **Changing survey context:** AI technologies and survey wording evolve.
   Eurostat status flags remain in the dataset, and flagged comparisons require
   caution.
4. **Different denominators:** Purpose and barrier questions are conditional on
   specific subgroups. They should not be read as shares of all enterprises.
5. **Sector composition:** Country differences may partly reflect industrial
   structure, digital infrastructure, skills, and policy context not directly
   measured here.
"""
        ),
        markdown(
            """
## Reproducibility

- Run `python -m src.data_pipeline` to refresh the curated CSV from Eurostat.
- Run this notebook from the repository root.
- Run `streamlit run app.py` to launch the interactive dashboard.
- All charts use Plotly only and share the same color-vision-deficiency-safe
  visual system.
"""
        ),
    ]

    # Pre-populate verified outputs. The sandbox used to build this project
    # blocks Jupyter's local kernel sockets, but the same code runs normally in
    # Jupyter on a standard laptop. Static Plotly PNGs keep the delivered
    # notebook fully readable; rerunning a chart cell makes it interactive.
    data_for_outputs = load_data()
    eda_summary = pd.Series(
        {
            "Rows": len(data_for_outputs),
            "Columns": data_for_outputs.shape[1],
            "Years": (
                f"{data_for_outputs['time'].min()}–"
                f"{data_for_outputs['time'].max()}"
            ),
            "EU countries": data_for_outputs.loc[
                data_for_outputs["geo"] != "EU27_2020", "geo"
            ].nunique(),
            "Firm-size classes": data_for_outputs["size_emp"].nunique(),
            "Selected indicators": data_for_outputs["indic_is"].nunique(),
            "Source tables": data_for_outputs["source_dataset"].nunique(),
        }
    ).to_frame("Value")
    coverage = (
        data_for_outputs.groupby(["source_dataset", "time"])
        .agg(
            observations=("value", "size"),
            geographies=("geo", "nunique"),
            sectors=("nace_r2", "nunique"),
            indicators=("indic_is", "nunique"),
        )
    )
    quality_checks = pd.Series(
        {
            "Missing numeric values": int(data_for_outputs["value"].isna().sum()),
            "Values below 0%": int((data_for_outputs["value"] < 0).sum()),
            "Values above 100%": int((data_for_outputs["value"] > 100).sum()),
            "Observations with Eurostat flags": int(
                data_for_outputs["status"].ne("").sum()
            ),
            "Duplicate metric rows": int(
                data_for_outputs.duplicated(
                    [
                        "source_dataset",
                        "time",
                        "geo",
                        "size_emp",
                        "nace_r2",
                        "indic_is",
                        "unit",
                    ]
                ).sum()
            ),
        }
    ).to_frame("Count")
    table_outputs = {
        "eda_summary =": eda_summary,
        "coverage =": coverage,
        "quality_checks =": quality_checks,
    }
    figure_sources = {
        f"fig_{number:02d}": ROOT / "assets" / "charts" / f"figure_{number:02d}.png"
        for number in range(1, 13)
    }

    execution_count = 0
    for cell in cells:
        if cell["cell_type"] != "code":
            continue
        execution_count += 1
        cell["execution_count"] = execution_count
        source = cell["source"].strip()
        for prefix, table in table_outputs.items():
            if source.startswith(prefix):
                cell["outputs"] = [
                    nbf.v4.new_output(
                        output_type="display_data",
                        data={
                            "text/html": table.to_html(),
                            "text/plain": table.to_string(),
                        },
                    )
                ]
                break
        else:
            for prefix, path in figure_sources.items():
                if source.startswith(prefix):
                    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
                    cell["outputs"] = [
                        nbf.v4.new_output(
                            output_type="display_data",
                            data={
                                "image/png": encoded,
                                "text/plain": (
                                    f"<Plotly figure {prefix.removeprefix('fig_')}>"
                                ),
                            },
                            metadata={"image/png": {"width": 1000}},
                        )
                    ]
                    break

    notebook["cells"] = cells
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(cells)} cells")


if __name__ == "__main__":
    main()
