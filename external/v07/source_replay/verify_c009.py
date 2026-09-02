from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/pydantic/pydantic-ai.git"
PRE_FIX = "194fb2ad5521b97a415709649a3618a27caa03fc"
POST_FIX = "2dbcf1dff61b439d4dcb9f027a764802cc669b6e"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from pydantic_ai import DeferredToolRequests, DeferredToolResults
from pydantic_ai.messages import ToolCallPart

approval = ToolCallPart("a", {}, tool_call_id="approval_1")
call = ToolCallPart("b", {}, tool_call_id="call_1")
requests = DeferredToolRequests(
    approvals=[approval],
    calls=[call],
    metadata={"approval_1": {"kind": "approval"}, "call_1": {"kind": "call"}},
)
mis_keyed = DeferredToolResults(
    approvals={"call_1": True},
    calls={"approval_1": "result"},
)
remaining = requests.remaining(mis_keyed)
print(json.dumps({
    "status": "ok",
    "remaining_is_none": remaining is None,
    "remaining_approval_ids": [] if remaining is None else [item.tool_call_id for item in remaining.approvals],
    "remaining_call_ids": [] if remaining is None else [item.tool_call_id for item in remaining.calls],
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
        ]
    )
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return observation == {
        "status": "ok",
        "remaining_is_none": True,
        "remaining_approval_ids": [],
        "remaining_call_ids": [],
    }


def _post_expected(observation: dict) -> bool:
    return observation == {
        "status": "ok",
        "remaining_is_none": False,
        "remaining_approval_ids": ["approval_1"],
        "remaining_call_ids": ["call_1"],
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c009-") as tmp:
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
            "case_id": "C009",
            "source": "pydantic/pydantic-ai#7626",
            "repository": "pydantic/pydantic-ai",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "bounded_interface": "DeferredToolRequests.remaining with identical approval/call requests and deliberately cross-category result IDs",
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
