from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/huggingface/smolagents.git"
PRE_FIX = "bae54fd37431c67c6704870cf6e8e5865b72930e"
POST_FIX = "1af07997acf5ac5539581e8faeb79a61f7513030"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from smolagents.local_python_executor import evaluate_python_code

code = """
try:
    final_answer(1)
except Exception:
    final_answer(2)
"""
try:
    result, is_final = evaluate_python_code(code, {"final_answer": lambda answer: answer}, state={})
except BaseException as exc:
    print(json.dumps({"status":"error","error_type":type(exc).__name__,"message":str(exc)}, sort_keys=True))
else:
    print(json.dumps({"status":"ok","result":result,"is_final":bool(is_final)}, sort_keys=True))
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
    with tempfile.TemporaryDirectory(prefix="v07-smol-1914-") as tmp:
        root = Path(tmp)
        repo = root / "smolagents"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root)
        post = replay(repo, POST_FIX, root)
        verified = (
            all(x == {"status":"ok","result":2,"is_final":True} for x in pre)
            and all(x == {"status":"ok","result":1,"is_final":True} for x in post)
        )
        print(json.dumps({"source":"huggingface/smolagents#1914","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
