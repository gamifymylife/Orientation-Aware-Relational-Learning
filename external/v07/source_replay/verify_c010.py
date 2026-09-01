from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/pydantic/pydantic-ai.git"
PRE_FIX = "1d7eb695cc17c5bed46d32749ed02092819fc3a1"
POST_FIX = "fc9e9264d04314078db02c9ed99959fe8c740464"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from typing import Annotated
from annotated_types import Ge, Le
from pydantic import BaseModel
from pydantic_ai.models.test import _JsonSchemaTestData

class Bounds(BaseModel):
    my_int_eq: Annotated[int, Ge(7), Le(7)]
    my_float_eq: Annotated[float, Ge(7.5), Le(7.5)]

try:
    data = _JsonSchemaTestData(Bounds.model_json_schema()).generate()
except Exception as exc:
    print(json.dumps({"status": "error", "error_type": type(exc).__name__, "message": str(exc)}))
else:
    print(json.dumps({"status": "ok", "data": data}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def _run_observation(python: Path, repo: Path) -> dict:
    completed = subprocess.run(
        [str(python), "-c", SNIPPET],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("revision produced no replay output")
    return json.loads(lines[-1])


def replay(repo: Path, revision: str, work: Path) -> list[dict]:
    run(["git", "checkout", "--force", revision], cwd=repo)
    env = work / f"venv-{revision[:8]}"
    run([sys.executable, "-m", "venv", str(env)])
    python = env / "bin" / "python"
    run([str(python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])

    # pydantic-ai-slim pins pydantic-graph to the exact same dynamic VCS version.
    # Install both sibling packages from the same checked-out revision so pip never
    # tries to resolve an unreleased dev build from PyPI.
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--quiet",
            "-e",
            str(repo / "pydantic_graph"),
            "-e",
            str(repo / "pydantic_ai_slim"),
        ]
    )
    return [_run_observation(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return observation.get("status") == "error" and observation.get("error_type") == "ZeroDivisionError"


def _post_expected(observation: dict) -> bool:
    return observation.get("status") == "ok" and observation.get("data") == {
        "my_int_eq": 7,
        "my_float_eq": 7.5,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c010-") as tmp:
        root = Path(tmp)
        repo = root / "pydantic-ai"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre_runs = replay(repo, PRE_FIX, root)
        post_runs = replay(repo, POST_FIX, root)

        expected = (
            all(_pre_expected(item) for item in pre_runs)
            and all(_post_expected(item) for item in post_runs)
            and len({json.dumps(item, sort_keys=True) for item in pre_runs}) == 1
            and len({json.dumps(item, sort_keys=True) for item in post_runs}) == 1
        )
        report = {
            "case_id": "C010",
            "source": "pydantic/pydantic-ai#7642",
            "repository": "pydantic/pydantic-ai",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": expected,
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        if not expected:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
