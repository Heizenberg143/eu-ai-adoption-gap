# Europe's AI Adoption Gap

**Data Visualization final project - Summer 2026**  
**Student:** Usaid Aamer

**Live dashboard:** [usaid-eu-ai-adoption-gap.streamlit.app](https://usaid-eu-ai-adoption-gap.streamlit.app/)  
**GitHub repository:** [Heizenberg143/eu-ai-adoption-gap](https://github.com/Heizenberg143/eu-ai-adoption-gap)

Europe's business use of artificial intelligence is accelerating, but the
benefits are not spreading evenly. This project asks:

> Can rapid AI adoption close Europe's business capability gap?

The analysis uses official Eurostat enterprise survey data for 2023-2025 to
compare adoption across 27 EU countries, firm sizes, economic sectors,
technologies, business purposes, and reported barriers.

## Headline findings

- EU enterprise AI adoption increased from **8.1% in 2023** to **20.0% in
  2025**.
- In 2025, **55.0% of large firms** used AI, compared with **17.0% of small
  firms** - a 38 percentage-point divide.
- Denmark led the EU at **42.0%**, while Romania was at **5.2%**.
- Information and communication reached **62.5%** adoption; construction was
  at **10.8%**.
- Among interested non-adopters, **70.3% cited a lack of expertise**. Cost
  ranked only sixth among the eight reported barriers.

The central conclusion is **acceleration without convergence**: adoption is
growing, but national, firm-size, and capability gaps remain wide.

## What is included

| Deliverable | Location |
|---|---|
| Reproducible Jupyter notebook | `notebooks/eu_ai_adoption_analysis.ipynb` |
| Browser-ready notebook export | `exports/eu_ai_adoption_analysis.html` |
| Streamlit dashboard | `app.py` |
| Final presentation | `presentation/eu_ai_adoption_gap.pptx` |
| Presentation PDF | `presentation/eu_ai_adoption_gap.pdf` |
| Curated analysis dataset | `data/processed/eu_ai_adoption_2023_2025.csv` |
| Data dictionary and metadata | `data/processed/codebook.json`, `data/processed/dataset_metadata.json` |
| Twelve publication-ready charts | `assets/charts/` |

## The 12 analytical questions

| # | Question | Main method |
|---:|---|---|
| 1 | How quickly is EU AI adoption changing by firm size? | Indexed time-series comparison |
| 2 | Are lower-adoption countries catching up with leaders? | Country comparison, 2023 vs 2025 |
| 3 | Did countries with higher 2024 adoption accelerate faster in 2025? | Scatterplot with change calculation |
| 4 | Where is the large-small firm adoption gap widest? | Country-level gap ranking |
| 5 | How deep is adoption: one AI technology or a broader stack? | Threshold comparison by firm size |
| 6 | Which technologies separate small and large AI adopters? | Technology mix comparison |
| 7 | Which sectors are leading, and which remain behind? | Sector change comparison |
| 8 | How are business uses of AI changing? | Purpose-level change comparison |
| 9 | Do sectors use AI for different business purposes? | Sector-purpose heatmap |
| 10 | Which low-adoption sectors contain the largest pool of interested non-users? | Adoption-versus-consideration matrix |
| 11 | Which barriers stop interested firms, and do they vary by size? | Barrier ranking by firm size |
| 12 | Are AI adopters also stronger in data analytics and cloud services? | Digital-foundation comparison |

## Data sources

The project uses two official Eurostat tables:

- [`isoc_eb_ai`](https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en):
  artificial intelligence use by enterprise size and country
- [`isoc_eb_ain2`](https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ain2/default/table?lang=en):
  artificial intelligence use by economic activity

The curated CSV contains **43,881 aggregate survey observations** for
2023-2025. It is about 3 MB and is comfortable to run on a MacBook Pro with
16 GB RAM.

### Important denominator note

Not every percentage uses the same base:

- Overall adoption values describe a share of **all enterprises** in scope.
- Technology and business-purpose values describe a share of **AI-adopting
  enterprises**.
- Barrier values describe firms that **considered AI but did not adopt it**.

The notebook and dashboard label these groups explicitly so unlike
percentages are not compared as if they had the same denominator.

## Run the project on a Mac

Open Terminal, move into this project folder, and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the dashboard:

```bash
streamlit run app.py
```

Streamlit will open the dashboard in your browser. To open the notebook:

```bash
jupyter notebook notebooks/eu_ai_adoption_analysis.ipynb
```

The processed dataset and exported outputs are already included. Rebuilding
is optional. The dashboard and notebook do not need Kaleido. Install the
separate export dependency only if you want to regenerate the PNG files:

```bash
pip install -r requirements-export.txt
python -m src.data_pipeline
python scripts/export_figures.py
python scripts/build_notebook.py
```

## Repository structure

```text
.
├── app.py
├── assets/charts/
├── data/
│   ├── raw/
│   └── processed/
├── exports/
├── notebooks/
├── presentation/
├── scripts/
└── src/
```

## Dashboard

The Streamlit app contains five tabs:

1. Overview
2. Firm-size divide
3. Sectors and use cases
4. Barriers
5. About the data

It includes a year filter, country selector, sector-purpose explorer, and
consistent color-safe Plotly styling.

**Live dashboard:** [https://usaid-eu-ai-adoption-gap.streamlit.app/](https://usaid-eu-ai-adoption-gap.streamlit.app/)

## Reproducibility

All transformations are in `src/data_pipeline.py`. The processed data retains
Eurostat status flags, and chart calculations are centralized in
`src/charts.py`. Raw Eurostat JSON responses are included so the current
analysis can be reproduced even if the API changes later.

The data was last reported by Eurostat as updated on **15 June 2026**.
