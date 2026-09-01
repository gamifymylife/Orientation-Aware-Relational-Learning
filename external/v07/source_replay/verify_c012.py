from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/langchain-ai/langgraph.git"
PRE_FIX = "ea5f9cc9fb8c4b123769daab4753af34de29b1e9"
POST_FIX = "a90ab4435853b8a5b6f82b20220b4c76af0e46d1"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json

from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

saver = InMemorySaver()
serde = JsonPlusSerializer()
thread_id, ns, channel = "t1", "", "messages"

v0 = "00000000000000000000000000000000.0"
v1 = "00000000000000000000000000000001.0"
v2 = "00000000000000000000000000000002.0"
v3 = "00000000000000000000000000000003.0"

saver.blobs[(thread_id, ns, channel, v0)] = serde.dumps_typed([])
saver.blobs[(thread_id, ns, channel, v1)] = serde.dumps_typed(["A"])
saver.blobs[(thread_id, ns, channel, v2)] = ("empty", b"")
saver.blobs[(thread_id, ns, channel, v3)] = ("empty", b"")

cp0 = empty_checkpoint()
cp0["id"] = "cp0"
cp0["channel_versions"][channel] = v0
cp1 = empty_checkpoint()
cp1["id"] = "cp1"
cp1["channel_versions"][channel] = v1
cp2 = empty_checkpoint()
cp2["id"] = "cp2"
cp2["channel_versions"][channel] = v2
cp3 = empty_checkpoint()
cp3["id"] = "cp3"
cp3["channel_versions"][channel] = v3

saver.storage[thread_id][ns] = {
    "cp0": (serde.dumps_typed(cp0), serde.dumps_typed({}), None),
    "cp1": (serde.dumps_typed(cp1), serde.dumps_typed({}), "cp0"),
    "cp2": (serde.dumps_typed(cp2), serde.dumps_typed({}), "cp1"),
    "cp3": (serde.dumps_typed(cp3), serde.dumps_typed({}), "cp2"),
}

saver.writes[(thread_id, ns, "cp0")][("task0", 0)] = (
    "task0", channel, serde.dumps_typed("OLDER-WRITE"), ""
)
saver.writes[(thread_id, ns, "cp1")][("task1", 0)] = (
    "task1", channel, serde.dumps_typed("PRE-DELTA-WRITE"), ""
)
saver.writes[(thread_id, ns, "cp2")][("task2", 0)] = (
    "task2", channel, serde.dumps_typed("B"), ""
)
saver.writes[(thread_id, ns, "cp3")][("task3", 0)] = (
    "task3", channel, serde.dumps_typed("PENDING-AT-TARGET"), ""
)

config = {
    "configurable": {
        "thread_id": thread_id,
        "checkpoint_ns": ns,
        "checkpoint_id": "cp3",
    }
}

try:
    result = saver.get_delta_channel_history(config=config, channels=[channel])[channel]
except Exception as exc:
    print(json.dumps({"status": "error", "error_type": type(exc).__name__, "message": str(exc)}))
else:
    values = [value for _, _, value in result["writes"]]
    print(json.dumps({"status": "ok", "seed": result.get("seed"), "writes": values}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def _observe(python: Path, repo: Path) -> dict:
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
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--quiet",
            "-e",
            str(repo / "libs" / "checkpoint"),
        ]
    )
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return observation == {
        "status": "ok",
        "seed": ["A"],
        "writes": ["B"],
    }


def _post_expected(observation: dict) -> bool:
    return observation == {
        "status": "ok",
        "seed": ["A"],
        "writes": ["PRE-DELTA-WRITE", "B"],
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c012-") as tmp:
        root = Path(tmp)
        repo = root / "langgraph"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre_runs = replay(repo, PRE_FIX, root)
        post_runs = replay(repo, POST_FIX, root)
        verified = (
            all(_pre_expected(item) for item in pre_runs)
            and all(_post_expected(item) for item in post_runs)
            and len({json.dumps(item, sort_keys=True) for item in pre_runs}) == 1
            and len({json.dumps(item, sort_keys=True) for item in post_runs}) == 1
        )
        print(
            json.dumps(
                {
                    "case_id": "C012",
                    "source": "langchain-ai/langgraph#8526",
                    "repository": "langchain-ai/langgraph",
                    "pre_fix_revision": PRE_FIX,
                    "post_fix_revision": POST_FIX,
                    "confirmation_repeats": CONFIRMATION_REPEATS,
                    "pre_fix_runs": pre_runs,
                    "post_fix_runs": post_runs,
                    "replay_verified": verified,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
