"""Write the synthetic Apple Health-shaped export to apple_health_export/export.xml and parse it back."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.adapters.apple_health import parse_export  # noqa: E402
from src.adapters.synthetic_export import build_synthetic_export  # noqa: E402

output = ROOT / "apple_health_export" / "export.xml"
output.parent.mkdir(exist_ok=True)
output.write_bytes(build_synthetic_export())
parsed = parse_export(str(output))
print(f"Synthetic export parsed: {len(parsed['daily'])} dates, cycle starts={parsed['cycle_starts']}")
