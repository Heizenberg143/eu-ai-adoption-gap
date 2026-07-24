# Data notes

## Processed dataset

`processed/eu_ai_adoption_2023_2025.csv` is the analysis-ready dataset used by
the notebook and dashboard.

- 43,881 rows
- 10 columns
- 2023-2025
- 27 EU countries plus the EU aggregate where available
- Official Eurostat aggregate survey percentages
- No firm-level or personally identifiable data

The included `codebook.json` maps Eurostat codes to readable labels.
`dataset_metadata.json` records the source tables, years, country count, and
source update date.

## Raw source files

- `raw/isoc_eb_ai_batch_1.json`
- `raw/isoc_eb_ai_batch_2.json`
- `raw/isoc_eb_ain2_eu27.json`

They are cached Eurostat JSON-stat responses for:

- [`isoc_eb_ai`](https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en)
- [`isoc_eb_ain2`](https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ain2/default/table?lang=en)

## Rebuild

From the project root:

```bash
python -m src.data_pipeline
```

This validates the year range, country coverage, percentage range, and missing
values before writing the processed files.
