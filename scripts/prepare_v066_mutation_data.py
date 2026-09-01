from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


SOURCE_COMMIT = "f8d8376e0efe345161f26ff6483a404c8548fe1c"
FROZEN_TARGETS = (
    ("Closure", 118),
    ("Lang", 33),
    ("Math", 22),
    ("Time", 6),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix_path(source_root: Path, project: str, fault: int) -> Path:
    return (
        source_root
        / "resources"
        / "matrices"
        / project
        / f"{project}.{fault}f.big.all.Matrix.csv"
    )


def convert(
    source_root: Path,
    source: Path,
    destination: Path,
    project: str,
    fault: int,
) -> dict[str, object]:
    with source.open(newline="") as handle:
        header = next(csv.reader(handle))
    mutant_ids = np.asarray(header[3:], dtype=str)
    frame = pd.read_csv(source, skiprows=[1])
    kills = frame.iloc[:, 3:].to_numpy(dtype=np.uint8)
    if not np.all((kills == 0) | (kills == 1)):
        raise ValueError(f"non-binary cell in {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        destination,
        project=np.asarray(project),
        fault=np.asarray(fault),
        test_types=frame.iloc[:, 0].astype(str).to_numpy(),
        test_names=frame.iloc[:, 1].astype(str).to_numpy(),
        mutant_ids=mutant_ids,
        kills=kills,
    )
    return {
        "project": project,
        "fault": fault,
        "source_relative_path": str(source.relative_to(source_root)),
        "source_sha256": sha256_file(source),
        "source_bytes": source.stat().st_size,
        "compact_file": destination.name,
        "compact_sha256": sha256_file(destination),
        "compact_bytes": destination.stat().st_size,
        "tests": int(kills.shape[0]),
        "mutants": int(kills.shape[1]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("external/mutation/v066/data"),
    )
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    rows = []
    for project, fault in FROZEN_TARGETS:
        source = matrix_path(source_root, project, fault)
        destination = args.out / f"{project.lower()}_{fault}.npz"
        rows.append(convert(source_root, source, destination, project, fault))

    manifest = {
        "source_repository": "https://github.com/donghwan-shin/Diversity-aware-Mutation-Testing",
        "source_commit": SOURCE_COMMIT,
        "source_license": "MIT",
        "selection_rule": "lowest SHA-256 v066-confirm:<project>:<fault> among metadata-eligible matrices",
        "matrices": rows,
    }
    manifest_path = args.out.parent / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
