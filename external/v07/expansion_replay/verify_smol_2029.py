from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/huggingface/smolagents.git"
PRE_FIX = "87f69c30778113c59f4658af187a8f3f55bd1d6f"
POST_FIX = "563dae88db4a5dd682c152a8ab22794b978935c9"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from smolagents.local_python_executor import evaluate_python_code

code = """
class MyContextManager:
    def __init__(self):
        self.exited = False
    def __enter__(self):
        return 'entered-value'
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exited = True
        return False
cm = MyContextManager()
with cm as val:
    marker = val
"""
state = {}
try:
    evaluate_python_code(code, {}, state=state)
except BaseException as exc:
    print(json.dumps({"status": "error", "error_type": type(exc).__name__, "message": str(exc)}, sort_keys=True))
else:
    cm = state.get("cm")
    print(json.dumps({"status": "ok", "marker": state.get("marker"), "exited": bool(getattr(cm, "exited", False))}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def observe(python: Path, repo: Path) -> dict:
    p = subprocess.run([str(python), "-c", SNIPPET], cwd=repo, capture_output=True, text=True)
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    if not lines:
        return {"status": "process_error", "returncode": p.returncode, "stderr": p.stderr[-2000:]}
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
    with tempfile.TemporaryDirectory(prefix="v07-smol-2029-") as tmp:
        root = Path(tmp)
        repo = root / "smolagents"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root)
        post = replay(repo, POST_FIX, root)
        verified = (
            all(x.get("status") == "error" for x in pre)
            and all(x == {"status": "ok", "marker": "entered-value", "exited": True} for x in post)
            and len({json.dumps(x, sort_keys=True) for x in pre}) == 1
            and len({json.dumps(x, sort_keys=True) for x in post}) == 1
        )
        print(json.dumps({"source":"huggingface/smolagents#2029","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
