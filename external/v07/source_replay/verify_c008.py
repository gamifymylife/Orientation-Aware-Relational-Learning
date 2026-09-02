from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/pydantic/pydantic-ai.git"
PRE_FIX = "6aee1c09bd065725ff14f21a15f731b0c3c88e0c"
POST_FIX = "eadbb525eda1f2f7473e868dd77850779ee1923f"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from datetime import datetime, timezone
from pydantic_evals.otel.span_tree import SpanNode

now = datetime(2026, 1, 1, tzinfo=timezone.utc)

def node(name, span_id, parent_span_id, depth):
    return SpanNode(
        name=name,
        trace_id=1,
        span_id=span_id,
        parent_span_id=parent_span_id,
        start_timestamp=now,
        end_timestamp=now,
        attributes={"depth": depth},
    )

root = node("root", 1, None, 0)
level1 = node("level1", 2, 1, 1)
level2 = node("level2", 3, 2, 2)
level3 = node("level3", 4, 3, 3)
leaf = node("leaf", 5, 4, 4)
root.add_child(level1)
level1.add_child(level2)
level2.add_child(level3)
level3.add_child(leaf)

query = {
    "all_descendants_have": {"has_attribute_keys": ["depth"]},
    "no_descendant_has": {"name_equals": "level2"},
    "stop_recursing_when": {"name_equals": "never-matches"},
}
print(json.dumps({
    "status": "ok",
    "matches": root.matches(query),
    "descendant_names": [item.name for item in root.descendants],
}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def _observe(python: Path, repo: Path) -> dict:
    completed = subprocess.run(
        [str(python), "-c", SNIPPET],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "revision replay failed\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
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
            "-e",
            str(repo / "pydantic_evals"),
        ]
    )
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and observation.get("matches") is True
        and observation.get("descendant_names") == ["level1", "level2", "level3", "leaf"]
    )


def _post_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and observation.get("matches") is False
        and observation.get("descendant_names") == ["level1", "level2", "level3", "leaf"]
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c008-") as tmp:
        root = Path(tmp)
        repo = root / "pydantic-ai"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre_runs = replay(repo, PRE_FIX, root)
        post_runs = replay(repo, POST_FIX, root)
        verified = (
            all(_pre_expected(item) for item in pre_runs)
            and all(_post_expected(item) for item in post_runs)
            and len({json.dumps(item, sort_keys=True) for item in pre_runs}) == 1
            and len({json.dumps(item, sort_keys=True) for item in post_runs}) == 1
        )
        print(json.dumps({
            "case_id": "C008",
            "source": "pydantic/pydantic-ai#7499",
            "repository": "pydantic/pydantic-ai",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "bounded_interface": "SpanNode.matches over an identical five-node span tree and multi-condition pruned query",
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
