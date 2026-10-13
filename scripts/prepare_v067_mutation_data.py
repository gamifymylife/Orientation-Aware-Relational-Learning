"""Prepare ONLY the four frozen v0.6.7 public mutation matrices.

No downloads, code execution from the source checkout, or model calls.
The operator must supply a clean, exact-commit checkout of the public
Diversity-aware-Mutation-Testing repository.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_read(*args: str) -> str:
    proc = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def convert(path: Path, destination: Path, item: dict, source_repo: str, commit: str) -> dict:
    # Historical source format: row 1 column labels, row 2 metadata (not a test),
    # then exactly raw_tests binary test-vs-mutant rows.
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream)
        header = next(rows)
        if len(header) < 5:
            raise ValueError(f"short header: {path.name}")
        if len(header) - 3 != item["metadata_raw_mutants"]:
            raise ValueError(f"source mutant count changed: {path.name}")
        next(rows)  # source metadata row; as in v0.6.6 converter
        test_types, test_names, values = [], [], []
        for line_number, row in enumerate(rows, start=3):
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError(f"source row width changed: {path.name}:{line_number}")
            raw = [v.strip() for v in row[3:]]
            if any(v not in ("0", "1") for v in raw):
                raise ValueError(f"nonbinary kill value at {path.name}:{line_number}")
            test_types.append(row[0])
            test_names.append(row[1])
            values.append([int(v) for v in raw])
    if len(values) != item["metadata_raw_tests"]:
        raise ValueError(f"source test count changed: {path.name} ({len(values)})")
    if len(set(header[3:])) != len(header[3:]):
        raise ValueError("duplicate mutant labels")
    if len(set(zip(test_types, test_names))) < 1:
        raise ValueError("missing test identifiers")
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        destination,
        project=np.asarray(item["project"]),
        fault=np.asarray(item["fault"]),
        test_types=np.asarray(test_types, dtype=str),
        test_names=np.asarray(test_names, dtype=str),
        mutant_ids=np.asarray(header[3:], dtype=str),
        kills=np.asarray(values, dtype=np.uint8),
    )
    return {
        "project": item["project"],
        "fault": item["fault"],
        "path": destination.name,
        "sha256": digest(destination),
        "source_relative_path": item["source_relative_path"],
        "source_sha256": digest(path),
        "source_git_blob_sha": item["source_git_blob_sha"],
        "upstream_commit": commit,
        "upstream_url": (
            source_repo.rstrip("/") + "/blob/" + commit + "/" +
            item["source_relative_path"]
        ),
        "raw_tests": len(values),
        "raw_mutants": len(header) - 3,
    }


def prepare(source_root: Path, selection_lock: Path, output: Path) -> dict:
    lock = json.loads(selection_lock.read_text(encoding="utf-8"))
    if lock.get("schema") != "oarl-v067-source-selection-lock-1":
        raise ValueError("wrong selection lock")
    if len(lock.get("candidates", [])) != 4:
        raise ValueError("frozen cohort must have exactly four members")
    source_root = source_root.resolve(strict=True)
    commit = str(lock["upstream_commit"])
    actual = git_read("-C", str(source_root), "rev-parse", "HEAD")
    if actual != commit:
        raise ValueError(f"wrong upstream checkout: expected {commit}, got {actual}")
    if output.exists():
        raise ValueError(f"refusing to overwrite existing output: {output}")
    verified = []
    for item in lock["candidates"]:
        rel = Path(item["source_relative_path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("unsafe source path")
        source = (source_root / rel).resolve(strict=True)
        if not source.is_relative_to(source_root) or source.stat().st_size != item["source_bytes"]:
            raise ValueError(f"source path or byte size mismatch: {rel}")
        blob = git_read("-C", str(source_root), "hash-object", str(source))
        if blob != item["source_git_blob_sha"]:
            raise ValueError(f"Git blob mismatch or modified source: {rel}")
        verified.append((item, source))
    output.mkdir(parents=True)
    data = output / "data"
    manifest = {
        "schema": "oarl-v067-development-manifest-1",
        "assets": [
            convert(src, data / f"{item['project'].lower()}_{item['fault']}.npz",
                    item, lock["source_repository"], commit)
            for item, src in verified
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument(
        "--selection-lock", type=Path,
        default=Path("evidence/v067/SELECTION_LOCK.json")
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.source_root, args.selection_lock, args.out)
    print(f"PREPARED {len(result['assets'])} frozen sources; no heldout outcomes disclosed")


if __name__ == "__main__":
    main()
