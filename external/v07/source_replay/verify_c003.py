from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/openai/openai-agents-python.git"
PRE_FIX = "7abe1544ff685e4030205795431ca35f28bc3707"
POST_FIX = "c8b0a92847a3eb156e2b95bc63b37f920fabafae"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
import warnings
from agents.function_schema import function_schema

def search(query: str, model_extra: str) -> str:
    return f"{query}:{model_extra}"

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    schema = function_schema(search, use_docstring_info=False)
parsed = schema.params_pydantic_model.model_validate({"query": "hello", "model_extra": "gpt-4.1"})
args, kwargs = schema.to_call_args(parsed)
result = search(*args, **kwargs)
print(json.dumps({"status": "ok", "args": args, "kwargs": kwargs, "result": result}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def _observe(python: Path, repo: Path) -> dict:
    completed = subprocess.run([str(python), "-c", SNIPPET], cwd=repo, check=True, capture_output=True, text=True)
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
    run([str(python), "-m", "pip", "install", "--quiet", "-e", str(repo)])
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return observation.get("status") == "ok" and observation.get("result") == "hello:None"


def _post_expected(observation: dict) -> bool:
    return observation.get("status") == "ok" and observation.get("result") == "hello:gpt-4.1"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c003-") as tmp:
        root = Path(tmp)
        repo = root / "openai-agents-python"
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
            "case_id": "C003",
            "source": "openai/openai-agents-python#4627",
            "repository": "openai/openai-agents-python",
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
