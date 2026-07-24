"""Render title-free Plotly figures sized for the presentation evidence frames."""

from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.charts import FIGURE_BUILDERS  # noqa: E402
from src.data import load_data  # noqa: E402


FIGURE_NUMBERS = [1, 2, 3, 4, 6, 7, 9, 10, 11, 12]


def main() -> None:
    output_dir = ROOT / "presentation" / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    data = load_data()

    for number in FIGURE_NUMBERS:
        figure = FIGURE_BUILDERS[number - 1](data)
        annotations = [
            annotation
            for annotation in list(figure.layout.annotations or [])
            if not str(annotation.text).startswith("Source:")
        ]
        figure.layout.annotations = tuple(annotations)
        bottom_margin = 130 if number == 9 else 85
        figure.update_layout(
            title=None,
            width=1200,
            height=520,
            margin={"l": 80, "r": 55, "t": 25, "b": bottom_margin},
            font={"family": "Arial, sans-serif", "size": 14, "color": "#172033"},
        )
        path = output_dir / f"chart_{number:02d}.png"
        figure.write_image(path, width=1200, height=520, scale=1.5)
        print(f"Rendered {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
