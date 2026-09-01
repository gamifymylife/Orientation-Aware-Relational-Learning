from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/crewAIInc/crewAI.git"
PRE_FIX = "cba6c036469cc10eb9a69fc9e5c00ed181978755"
POST_FIX = "eda584a9d7dfd23144226816935d54f04a8d1c55"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from typing import Any

from crewai.agent import Agent
from crewai.agent.utils import handle_reasoning
from crewai.hooks.dispatch import HookAborted, InterceptionPoint, clear_all, on
from crewai.llm import LLM
from crewai.task import Task

clear_all()
denied = []

@on(InterceptionPoint.PRE_MODEL_CALL)
def deny(ctx: Any) -> None:
    denied.append("deny")
    raise HookAborted(reason="no model calls allowed", source="policy")

llm = LLM(model="gpt-4o-mini")
agent = Agent(
    role="Planner",
    goal="Plan work",
    backstory="You plan.",
    llm=llm,
    planning=True,
)
task = Task(description="Do the thing", expected_output="A result.", agent=agent)
outcome = "returned"
error_type = None
error_reason = None
try:
    handle_reasoning(agent, task)
except Exception as exc:
    outcome = "raised"
    error_type = type(exc).__name__
    error_reason = getattr(exc, "reason", str(exc))
finally:
    clear_all()

print(json.dumps({
    "status": "ok",
    "outcome": outcome,
    "error_type": error_type,
    "error_reason": error_reason,
    "deny_count": len(denied),
    "planning_appended": "\n\nPlanning:\n" in task.description,
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
    for line in reversed(completed.stdout.splitlines()):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("status") == "ok":
            return value
    raise RuntimeError(f"revision produced no JSON replay output\nstdout:\n{completed.stdout}")


def replay(repo: Path, revision: str, work: Path) -> list[dict]:
    run(["git", "checkout", "--force", revision], cwd=repo)
    env = work / f"venv-{revision[:8]}"
    run([sys.executable, "-m", "venv", str(env)])
    python = env / "bin" / "python"
    run([str(python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
    run([str(python), "-m", "pip", "install", "--quiet", "-e", str(repo / "lib" / "crewai")])
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and observation.get("outcome") == "returned"
        and observation.get("deny_count") == 0
        and observation.get("planning_appended") is True
    )


def _post_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and observation.get("outcome") == "raised"
        and observation.get("error_type") == "HookAborted"
        and observation.get("error_reason") == "no model calls allowed"
        and observation.get("deny_count") == 1
        and observation.get("planning_appended") is False
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c016-") as tmp:
        root = Path(tmp)
        repo = root / "crewai"
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
            "case_id": "C016",
            "source": "crewAIInc/crewAI#7111",
            "repository": "crewAIInc/crewAI",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "bounded_interface": "legacy handle_reasoning planning path with the same local pre-model-call policy hook that raises HookAborted before provider execution",
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
