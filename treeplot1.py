from __future__ import annotations

import argparse
import csv
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()

DEFAULT_SOURCE = Path(
    r"G:\Shared drives\Team - Accounting"
)
DEFAULT_OUTPUT = SCRIPT_DIR / "test_updated_hierarchy3.csv"


def collect_rows(source: Path, include_directories: bool) -> list[dict[str, str | int | list[str]]]:
    rows: list[dict[str, str | int | list[str]]] = []

    paths = [source, *source.rglob("*")]
    paths.sort(key=lambda p: tuple(part.lower() for part in p.relative_to(source).parts))

    for path in paths:
        is_dir = path.is_dir()
        if not include_directories and is_dir:
            continue

        if path == source:
            relative_path = "."
            parent = ""
        else:
            rel = path.relative_to(source)
            relative_path = str(rel)
            parent = str(rel.parent) if rel.parent != Path(".") else ""

        hierarchy_parts = [source.name]
        if path != source:
            hierarchy_parts.extend(path.relative_to(source).parts)

        rows.append(
            {
                "item_type": "directory" if is_dir else "file",
                "name": path.name if path != source else source.name,
                "full_path": str(path),
                "relative_path": relative_path,
                "parent_path": parent,
                "depth": len(hierarchy_parts) - 1,
                "extension": path.suffix.lower() if path.is_file() else "",
                "hierarchy_parts": hierarchy_parts,
            }
        )

    return rows


def write_csv(rows: list[dict[str, str | int | list[str]]], output: Path) -> None:
    max_levels = max((len(row["hierarchy_parts"]) for row in rows), default=0)
    hierarchy_columns = [f"level_{i}" for i in range(max_levels)]

    fieldnames = [
        "item_type",
        "name",
        "full_path",
        "relative_path",
        "parent_path",
        "depth",
        "extension",
        *hierarchy_columns,
    ]

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            csv_row = {key: row[key] for key in fieldnames if key in row}
            hierarchy = row["hierarchy_parts"]
            for idx, part in enumerate(hierarchy):
                csv_row[f"level_{idx}"] = part
            writer.writerow(csv_row)


def export_hierarchy(source: Path, output: Path, include_directories: bool, label: str) -> int:
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"{label} source folder not found: {source}")

    rows = collect_rows(source=source, include_directories=include_directories)
    write_csv(rows=rows, output=output)
    print(f"{label} CSV created: {output.resolve()}")
    print(f"{label} rows written: {len(rows)}")
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export file/folder hierarchy to a CSV file."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Source folder to scan (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--include-directories",
        action="store_true",
        default=True,  # Now always includes directories by default
        help="Include directories in CSV rows (files are always included).",
    )
    args = parser.parse_args()

    export_hierarchy(
        source=args.source,
        output=args.output,
        include_directories=args.include_directories,
        label="Hierarchy",
    )


if __name__ == "__main__":
    main()