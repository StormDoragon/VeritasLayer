from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    output = {
        "status": "stub",
        "message": "Benchmark pipeline will be implemented in a later phase.",
    }
    destination = Path("benchmarks/results")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "report.json").write_text(json.dumps(output, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
