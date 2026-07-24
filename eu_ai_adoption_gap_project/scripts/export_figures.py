"""Render every Plotly figure to PNG for the deck and README."""

from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore", message="Support for Kaleido versions")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.charts import FIGURE_BUILDERS  # noqa: E402
from src.data import load_data  # noqa: E402


def main() -> None:
    output_dir = ROOT / "assets" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)
    data = load_data()

    for number, builder in enumerate(FIGURE_BUILDERS, start=1):
        figure = builder(data)
        path = output_dir / f"figure_{number:02d}.png"
        figure.write_image(path, width=1200, height=figure.layout.height, scale=1.5)
        print(f"Rendered {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
