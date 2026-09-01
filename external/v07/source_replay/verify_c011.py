from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/pydantic/pydantic-ai.git"
PRE_FIX = "ae37b7fd495a934e7d8322ce81836ee6c3868aa6"
POST_FIX = "49a4e6f5aeb62936d5134ea5aff644263248b754"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from cohere import AssistantMessageResponse, ChatResponse, ToolCallV2, ToolCallV2Function
from pydantic_ai.models.cohere import CohereModel
from pydantic_ai.providers.cohere import CohereProvider

response = ChatResponse(
    id="123",
    finish_reason="COMPLETE",
    message=AssistantMessageResponse(
        content=None,
        role="assistant",
        tool_calls=[
            ToolCallV2(
                id="tc-1",
                function=ToolCallV2Function(arguments=None, name="get_current_time"),
                type="function",
            )
        ],
    ),
    usage=None,
)

try:
    model = CohereModel("command-r7b-12-2024", provider=CohereProvider(api_key="not-used"))
    result = model._process_response(response)
except Exception as exc:
    print(json.dumps({"status": "error", "error_type": type(exc).__name__, "message": str(exc)}))
else:
    parts = []
    for part in result.parts:
        item = {"type": type(part).__name__}
        if type(part).__name__ == "ToolCallPart":
            item.update({"tool_name": part.tool_name, "args": part.args, "tool_call_id": part.tool_call_id})
        parts.append(item)
    print(json.dumps({"status": "ok", "parts": parts}, sort_keys=True))
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
            str(python), "-m", "pip", "install", "--quiet",
            "-e", str(repo / "pydantic_graph"),
            "-e", f"{repo / 'pydantic_ai_slim'}[cohere]",
        ]
    )
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return observation == {"status": "ok", "parts": []}


def _post_expected(observation: dict) -> bool:
    return observation == {
        "status": "ok",
        "parts": [
            {
                "type": "ToolCallPart",
                "tool_name": "get_current_time",
                "args": None,
                "tool_call_id": "tc-1",
            }
        ],
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c011-") as tmp:
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
            "case_id": "C011",
            "source": "pydantic/pydantic-ai#7720",
            "repository": "pydantic/pydantic-ai",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
