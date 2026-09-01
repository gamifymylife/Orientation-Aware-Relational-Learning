from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/huggingface/smolagents.git"
PRE_FIX = "8b1dd44010f749d451c4fc9bdfa9eef0ba130baf"
POST_FIX = "26c733c745007e6f5e84b1fccc6f7be125e4ccc5"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from unittest.mock import MagicMock
from smolagents.agents import MultiStepAgent

try:
    agent = MultiStepAgent(tools=[], model=MagicMock())
    agent.run("Test task", single_step=True)
except BaseException as exc:
    print(json.dumps({"status":"error","error_type":type(exc).__name__,"message":str(exc)}, sort_keys=True))
else:
    print(json.dumps({"status":"ok","has_step_number":hasattr(agent,"step_number"),"step_number":getattr(agent,"step_number",None)}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def observe(python: Path, repo: Path) -> dict:
    p = subprocess.run([str(python), "-c", SNIPPET], cwd=repo, capture_output=True, text=True)
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    if not lines:
        return {"status":"process_error","returncode":p.returncode,"stderr":p.stderr[-2000:]}
    return json.loads(lines[-1])


def replay(repo: Path, revision: str, root: Path) -> list[dict]:
    run(["git", "checkout", "--force", revision], cwd=repo)
    env = root / f"venv-{revision[:8]}"
    run([sys.executable, "-m", "venv", str(env)])
    py = env / "bin" / "python"
    run([str(py), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "--quiet", "-e", str(repo)])
    return [observe(py, repo) for _ in range(CONFIRMATION_REPEATS)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="v07-smol-495-") as tmp:
        root = Path(tmp)
        repo = root / "smolagents"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root)
        post = replay(repo, POST_FIX, root)
        verified = (
            all(x == {"status":"ok","has_step_number":False,"step_number":None} for x in pre)
            and all(x == {"status":"ok","has_step_number":True,"step_number":1} for x in post)
        )
        print(json.dumps({"source":"huggingface/smolagents#495","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
