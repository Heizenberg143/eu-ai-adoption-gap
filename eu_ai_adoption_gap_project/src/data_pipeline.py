"""Download and prepare the Eurostat AI adoption data used in the project.

The pipeline deliberately requests a narrow slice of two official Eurostat
tables. This keeps the final dataset lightweight while retaining the dimensions
needed for country, firm-size, sector, technology, purpose, and barrier analysis.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
API_ROOT = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
)

EU27 = [
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

ISO3 = {
    "AT": "AUT",
    "BE": "BEL",
    "BG": "BGR",
    "HR": "HRV",
    "CY": "CYP",
    "CZ": "CZE",
    "DK": "DNK",
    "EE": "EST",
    "FI": "FIN",
    "FR": "FRA",
    "DE": "DEU",
    "EL": "GRC",
    "HU": "HUN",
    "IE": "IRL",
    "IT": "ITA",
    "LV": "LVA",
    "LT": "LTU",
    "LU": "LUX",
    "MT": "MLT",
    "NL": "NLD",
    "PL": "POL",
    "PT": "PRT",
    "RO": "ROU",
    "SK": "SVK",
    "SI": "SVN",
    "ES": "ESP",
    "SE": "SWE",
    "EU27_2020": "EU27_2020",
}

INDICATORS = [
    # Adoption and maturity
    "E_AI_TANY",
    "E_AI_TX",
    "E_AI_TGE2",
    "E_AI_TGE3",
    # Technologies
    "E_AI_TTM",
    "E_AI_TSR",
    "E_AI_TNLG",
    "E_AI_TIR",
    "E_AI_TML",
    "E_AI_TPA",
    "E_AI_TAR",
    "E_AI_TPVSG",
    # Business purposes
    "E_AI_PMS",
    "E_AI_PPP",
    "E_AI_PBAM",
    "E_AI_PLOG",
    "E_AI_PITS",
    "E_AI_PFIN",
    "E_AI_PRDI",
    "E_AI_P1GE2",
    "E_AI_P1GE3",
    # Acquisition routes
    "E_AI_ADOWN",
    "E_AI_AMOWN",
    "E_AI_AOS",
    "E_AI_ARDY",
    "E_AI_AEXT",
    # Consideration and barriers
    "E_AI_EC",
    "E_AI_BCST",
    "E_AI_BLE",
    "E_AI_BINC",
    "E_AI_BDDT",
    "E_AI_BCDP",
    "E_AI_BLEG",
    "E_AI_BEC",
    "E_AI_BNU",
    # Digital foundations
    "E_AI_DA",
    "E_AI_CC",
]

SIZE_CODES = ["10-49", "50-249", "GE250", "GE10"]
UNIT_CODES = [
    "PC_ENT",
    "PC_ENT_IUSE",
    "PC_ENT_AI_EC",
    "PC_ENT_AI_TANY",
    "PC_ENT_AI_TX",
    "PC_ENT_AI_PDI",
]


def _chunks(items: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def _download_json(
    dataset: str,
    params: list[tuple[str, str]],
    destination: Path,
    retries: int = 3,
) -> dict[str, Any]:
    """Download one JSON-stat response and retain it for reproducibility."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    url = f"{API_ROOT}/{dataset}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "eu-ai-adoption-class-project/1.0"})

    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=90) as response:
                payload = response.read()
            destination.write_bytes(payload)
            data = json.loads(payload)
            data["_request_url"] = url
            return data
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            if attempt == retries:
                raise
            time.sleep(attempt * 2)
    raise RuntimeError("Unreachable")


def _ordered_codes(category_index: Any) -> list[str]:
    if isinstance(category_index, list):
        return list(category_index)
    return [
        code
        for code, _position in sorted(
            category_index.items(), key=lambda item: item[1]
        )
    ]


def jsonstat_to_frame(
    payload: dict[str, Any],
    source_dataset: str,
) -> pd.DataFrame:
    """Convert the sparse JSON-stat 2.0 response into a tidy DataFrame."""

    dimensions = payload["id"]
    sizes = payload["size"]
    dimension_codes: dict[str, list[str]] = {}
    dimension_labels: dict[str, dict[str, str]] = {}

    for dimension in dimensions:
        category = payload["dimension"][dimension]["category"]
        dimension_codes[dimension] = _ordered_codes(category["index"])
        dimension_labels[dimension] = category.get("label", {})

    values = payload.get("value", {})
    statuses = payload.get("status", {})
    if isinstance(values, list):
        value_items = enumerate(values)
    else:
        value_items = ((int(key), value) for key, value in values.items())

    rows: list[dict[str, Any]] = []
    for flat_index, value in value_items:
        if value is None:
            continue

        remainder = flat_index
        coordinates = [0] * len(sizes)
        for position in range(len(sizes) - 1, -1, -1):
            coordinates[position] = remainder % sizes[position]
            remainder //= sizes[position]

        row: dict[str, Any] = {
            dimension: dimension_codes[dimension][coordinate]
            for dimension, coordinate in zip(dimensions, coordinates)
        }
        row["value"] = float(value)
        if isinstance(statuses, list):
            row["status"] = statuses[flat_index] if flat_index < len(statuses) else ""
        else:
            row["status"] = statuses.get(str(flat_index), "")
        row["source_dataset"] = source_dataset
        row["source_updated"] = payload.get("updated", "")
        row["source_url"] = payload.get("_request_url", "")
        rows.append(row)

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    label_names = {
        "geo": "geo_label",
        "size_emp": "size_label",
        "nace_r2": "sector_label",
        "indic_is": "indicator_label",
        "unit": "unit_label",
    }
    for dimension, output_name in label_names.items():
        if dimension in frame.columns:
            frame[output_name] = frame[dimension].map(
                dimension_labels.get(dimension, {})
            )

    frame["iso_alpha"] = frame.get("geo", pd.Series(index=frame.index)).map(ISO3)
    frame["time"] = frame["time"].astype(int)
    return frame


def build_dataset(force_download: bool = False) -> pd.DataFrame:
    """Build and save the curated country-and-sector dataset."""

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    frames: list[pd.DataFrame] = []

    common_params = [
        ("lang", "en"),
        ("sinceTimePeriod", "2023"),
        *[("size_emp", code) for code in SIZE_CODES],
        *[("indic_is", code) for code in INDICATORS],
        *[("unit", code) for code in UNIT_CODES],
    ]

    # The API limits response cube size. Two modest country batches stay below
    # that limit while producing one combined tidy table.
    country_geos = ["EU27_2020", *EU27]
    for batch_number, geo_batch in enumerate(_chunks(country_geos, 14), start=1):
        path = RAW_DIR / f"isoc_eb_ai_batch_{batch_number}.json"
        if path.exists() and not force_download:
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload.setdefault(
                "_request_url",
                f"{API_ROOT}/isoc_eb_ai (cached country batch {batch_number})",
            )
        else:
            params = [*common_params, *[("geo", geo) for geo in geo_batch]]
            payload = _download_json("isoc_eb_ai", params, path)
        frames.append(jsonstat_to_frame(payload, "isoc_eb_ai"))

    sector_path = RAW_DIR / "isoc_eb_ain2_eu27.json"
    if sector_path.exists() and not force_download:
        payload = json.loads(sector_path.read_text(encoding="utf-8"))
        payload.setdefault(
            "_request_url",
            f"{API_ROOT}/isoc_eb_ain2 (cached EU27 sector slice)",
        )
    else:
        sector_params = [
            ("lang", "en"),
            ("sinceTimePeriod", "2023"),
            ("size_emp", "GE10"),
            *[("indic_is", code) for code in INDICATORS],
            *[("unit", code) for code in UNIT_CODES],
            ("geo", "EU27_2020"),
        ]
        payload = _download_json("isoc_eb_ain2", sector_params, sector_path)
    frames.append(jsonstat_to_frame(payload, "isoc_eb_ain2"))

    data = pd.concat(frames, ignore_index=True)
    data = data.drop_duplicates(
        subset=[
            "source_dataset",
            "size_emp",
            "nace_r2",
            "indic_is",
            "unit",
            "geo",
            "time",
        ],
        keep="last",
    )
    data = data.sort_values(
        ["source_dataset", "time", "geo", "size_emp", "nace_r2", "indic_is", "unit"]
    ).reset_index(drop=True)

    # Keep the student-facing CSV compact. Descriptive labels live in the
    # codebook instead of being repeated tens of thousands of times.
    output_columns = [
        "source_dataset",
        "time",
        "geo",
        "iso_alpha",
        "size_emp",
        "nace_r2",
        "indic_is",
        "unit",
        "value",
        "status",
    ]
    output = PROCESSED_DIR / "eu_ai_adoption_2023_2025.csv"
    data[output_columns].to_csv(output, index=False)

    codebook = {}
    for code_column, label_column in [
        ("geo", "geo_label"),
        ("size_emp", "size_label"),
        ("nace_r2", "sector_label"),
        ("indic_is", "indicator_label"),
        ("unit", "unit_label"),
    ]:
        lookup = (
            data[[code_column, label_column]]
            .dropna()
            .drop_duplicates(code_column)
            .sort_values(code_column)
        )
        codebook[code_column] = dict(
            zip(lookup[code_column], lookup[label_column])
        )
    (PROCESSED_DIR / "codebook.json").write_text(
        json.dumps(codebook, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    metadata = {
        "title": "EU enterprise AI adoption, 2023-2025",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "rows": int(len(data)),
        "columns": output_columns,
        "datasets": ["isoc_eb_ai", "isoc_eb_ain2"],
        "years": sorted(data["time"].unique().tolist()),
        "countries": int(data.loc[data["geo"].isin(EU27), "geo"].nunique()),
        "source_updated": sorted(data["source_updated"].dropna().unique().tolist()),
        "notes": [
            "Values are aggregate survey percentages, not firm-level observations.",
            "Eurostat status flags are retained in the status column.",
            "The Greek Eurostat code EL is mapped to ISO3 code GRC for consistent country identifiers.",
        ],
    }
    (PROCESSED_DIR / "dataset_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    return data


def validate_dataset(data: pd.DataFrame) -> None:
    """Fail loudly when the slice is incomplete or structurally unexpected."""

    required = {
        "source_dataset",
        "geo",
        "geo_label",
        "size_emp",
        "indic_is",
        "unit",
        "time",
        "value",
        "status",
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    years = set(data["time"].unique())
    if years != {2023, 2024, 2025}:
        raise ValueError(f"Expected years 2023-2025, found {sorted(years)}")

    found_countries = set(data.loc[data["geo"].isin(EU27), "geo"].unique())
    if found_countries != set(EU27):
        missing_countries = sorted(set(EU27) - found_countries)
        raise ValueError(f"Missing EU countries: {missing_countries}")

    if data["value"].isna().any():
        raise ValueError("The tidy dataset contains null numeric values")
    if not data["value"].between(0, 100).all():
        raise ValueError("A percentage is outside the expected 0-100 range")

    adoption = data[
        (data["source_dataset"] == "isoc_eb_ai")
        & (data["geo"] == "EU27_2020")
        & (data["size_emp"] == "GE10")
        & (data["indic_is"] == "E_AI_TANY")
        & (data["unit"] == "PC_ENT")
    ]
    if adoption["time"].nunique() != 3:
        raise ValueError("EU adoption headline is incomplete")


if __name__ == "__main__":
    dataset = build_dataset()
    validate_dataset(dataset)
    print(
        f"Prepared {len(dataset):,} rows across "
        f"{dataset['geo'].nunique()} geographies and "
        f"{dataset['time'].nunique()} years."
    )
