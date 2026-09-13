from __future__ import annotations

import argparse
from pathlib import Path
from ui_constraints import build_constraints, save_constraints


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Build valid Flask dropdown relationships from the same "
            "dataset used for CSAT model training."
        )
    )
    parser.add_argument("dataset", help="Training/source CSV/XLSX/XLS path")
    parser.add_argument(
        "--output",
        default="ui_constraints.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    payload = build_constraints(Path(args.dataset))
    output = save_constraints(payload, Path(args.output))

    print("Created:", output.resolve())
    print("Source:", payload["source_dataset"])
    print(
        "Category mappings:",
        len(payload["category_to_subcategories"]),
    )
    print(
        "Manager mappings:",
        len(payload["manager_to_supervisors"]),
    )
    print("Run: python app.py")


if __name__ == "__main__":
    main()
