"""Data-loading and metric-selection helpers used by the notebook and app."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "eu_ai_adoption_2023_2025.csv"
CODEBOOK_PATH = ROOT / "data" / "processed" / "codebook.json"

COUNTRY_SOURCE = "isoc_eb_ai"
SECTOR_SOURCE = "isoc_eb_ain2"
ALL_ACTIVITIES = "C10-S951_X_K"
EU = "EU27_2020"

EU27_CODES = [
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "EL",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
]

HIGH_LEVEL_SECTORS = [
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "L",
    "M",
    "N",
]

SECTOR_SHORT = {
    "C": "Manufacturing",
    "D": "Energy",
    "E": "Water & waste",
    "F": "Construction",
    "G": "Wholesale & retail",
    "H": "Transport & storage",
    "I": "Accommodation & food",
    "J": "Information & comms",
    "L": "Real estate",
    "M": "Professional & technical",
    "N": "Admin & support",
}

SIZE_SHORT = {
    "GE10": "All firms (10+)",
    "10-49": "Small (10–49)",
    "50-249": "Medium (50–249)",
    "GE250": "Large (250+)",
}


def load_codebook() -> dict:
    return json.loads(CODEBOOK_PATH.read_text(encoding="utf-8"))


def load_data() -> pd.DataFrame:
    data = pd.read_csv(
        DATA_PATH,
        dtype={
            "source_dataset": "string",
            "geo": "string",
            "iso_alpha": "string",
            "size_emp": "string",
            "nace_r2": "string",
            "indic_is": "string",
            "unit": "string",
            "status": "string",
        },
        keep_default_na=False,
    )
    codebook = load_codebook()
    for code_column, label_column in [
        ("geo", "geo_label"),
        ("size_emp", "size_label"),
        ("nace_r2", "sector_label"),
        ("indic_is", "indicator_label"),
        ("unit", "unit_label"),
    ]:
        data[label_column] = data[code_column].map(codebook[code_column])
    data["size_short"] = data["size_emp"].map(SIZE_SHORT).fillna(data["size_label"])
    data["sector_short"] = (
        data["nace_r2"].map(SECTOR_SHORT).fillna(data["sector_label"])
    )
    return data


def metric(
    data: pd.DataFrame,
    *,
    indicator: str,
    unit: str,
    source: str = COUNTRY_SOURCE,
    geo: str | list[str] | None = None,
    size: str | list[str] | None = None,
    sector: str | list[str] | None = None,
    year: int | list[int] | None = None,
) -> pd.DataFrame:
    """Return one explicitly defined metric slice.

    Explicit units are essential here because Eurostat publishes several
    denominator variants for the same indicator.
    """

    query = data[
        data["source_dataset"].eq(source)
        & data["indic_is"].eq(indicator)
        & data["unit"].eq(unit)
    ].copy()

    filters = {
        "geo": geo,
        "size_emp": size,
        "nace_r2": sector,
        "time": year,
    }
    for column, value in filters.items():
        if value is None:
            continue
        if isinstance(value, list):
            query = query[query[column].isin(value)]
        else:
            query = query[query[column].eq(value)]
    return query.reset_index(drop=True)


def assert_unique(
    frame: pd.DataFrame, keys: list[str], context: str
) -> pd.DataFrame:
    duplicates = frame.duplicated(keys, keep=False)
    if duplicates.any():
        raise ValueError(
            f"{context} has duplicate observations for keys {keys}: "
            f"{frame.loc[duplicates, keys].head().to_dict('records')}"
        )
    return frame

