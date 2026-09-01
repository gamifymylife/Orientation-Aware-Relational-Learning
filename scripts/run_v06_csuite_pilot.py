from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

import numpy as np

from oarl_bench.competitive import exact_duplicate_baseline, similarity_baseline
from oarl_bench.csuite import (
    all_oracle_pair_scores,
    discovery_signatures,
    load_csuite_interventions,
)


PILOT_DATASETS = ("lingauss", "nonlin_simpson", "cat_to_cts")
RELEASE = "v0.1"
BASE_URL = f"https://github.com/microsoft/csuite/releases/download/{RELEASE}"


def _download_release_interventions(dataset: str, destination: Path) -> tuple[str, str]:
    """Download the pinned CSuite release ZIP and extract interventions.json.

    GitHub release assets are used instead of the historical Azure mirror so the
    external pilot is reproducible from the same upstream repository/version cited
    by CSuite itself.
    """

    url = f"{BASE_URL}/csuite_{dataset}.zip"
    request = urllib.request.Request(url, headers={"User-Agent": "oarl-v06-pilot"})
    with urllib.request.urlopen(request, timeout=120) as response:
        archive_bytes = response.read()
    archive_sha256 = hashlib.sha256(archive_bytes).hexdigest()

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        candidates = [
            name for name in archive.namelist() if name.rstrip("/").endswith("interventions.json")
        ]
        if len(candidates) != 1:
            raise RuntimeError(
                f"expected exactly one interventions.json in {dataset} release archive; "
                f"found {candidates}"
            )
        data = archive.read(candidates[0])

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return archive_sha256, hashlib.sha256(data).hexdigest()


def _finite(values: list[float]) -> list[float]:
    return [value for value in values if np.isfinite(value)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the preregistered CSuite v0.6 pilot adapter check")
    parser.add_argument("--out", type=Path, default=Path("evidence/v06/pilot_outputs"))
    parser.add_argument("--cache", type=Path, default=Path(".cache/csuite-v0.1"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {
        "upstream": "microsoft/csuite",
        "upstream_release": RELEASE,
        "purpose": "adapter/pilot only; not confirmatory evidence",
        "pilot_datasets": list(PILOT_DATASETS),
        "files": {},
    }
    system_rows: list[dict[str, object]] = []
    oracle_rows: list[dict[str, object]] = []

    for dataset in PILOT_DATASETS:
        path = args.cache / dataset / "interventions.json"
        url = f"{BASE_URL}/csuite_{dataset}.zip"
        archive_sha256, interventions_sha256 = _download_release_interventions(dataset, path)
        manifest["files"][dataset] = {
            "release_asset_url": url,
            "release_archive_sha256": archive_sha256,
            "interventions_sha256": interventions_sha256,
        }

        views = load_csuite_interventions(path, system_id=dataset)
        signatures = discovery_signatures(views)
        oracle = all_oracle_pair_scores(views)
        exact = exact_duplicate_baseline(signatures)
        similarity = similarity_baseline(
            signatures,
            max_normalized_rmse=0.20,
            abstention_band=0.05,
        )

        nrmse_values = _finite([row.nrmse for row in oracle])
        corr_values = _finite([row.correlation for row in oracle])
        system_rows.append(
            {
                "dataset": dataset,
                "views": len(views),
                "pairs": len(oracle),
                "oracle_nrmse_min": min(nrmse_values) if nrmse_values else None,
                "oracle_nrmse_median": float(np.median(nrmse_values)) if nrmse_values else None,
                "oracle_correlation_max": max(corr_values) if corr_values else None,
                "exact_equivalent_calls": sum(p.decision.value == "equivalent" for p in exact),
                "similarity_equivalent_calls": sum(p.decision.value == "equivalent" for p in similarity),
                "similarity_unknown_calls": sum(p.decision.value == "unknown" for p in similarity),
            }
        )
        oracle_rows.extend(
            {
                "dataset": dataset,
                "left": row.left,
                "right": row.right,
                "nrmse": row.nrmse,
                "correlation": row.correlation,
                "scale": row.scale,
                "offset": row.offset,
            }
            for row in oracle
        )

    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (args.out / "summary.json").write_text(json.dumps(system_rows, indent=2, sort_keys=True) + "\n")

    with (args.out / "oracle_pair_scores.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["dataset", "left", "right", "nrmse", "correlation", "scale", "offset"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(oracle_rows)

    print(json.dumps(system_rows, indent=2, sort_keys=True))
    print("PILOT ONLY: these outputs may calibrate a later frozen confirmatory protocol; they are not a v0.6 pass/fail result.")


if __name__ == "__main__":
    main()
