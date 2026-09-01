from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/openai/openai-agents-python.git"
PRE_FIX = "09814320a13843196489de7e6be21d30d1e29ec4"
POST_FIX = "2b81a9e32708b276846a0cd3721c42e6fb4067e2"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from typing import Any
from agents.function_schema import function_schema

def f(*, opt: int = 1, **kw: Any):
    return opt, kw

fs = function_schema(f, strict_json_schema=False, use_docstring_info=False)
parsed = fs.params_pydantic_model(**{"opt": 5, "kw": {"opt": 9}})
try:
    args, kwargs = fs.to_call_args(parsed)
except BaseException as exc:
    print(json.dumps({"status":"error","error_type":type(exc).__name__,"message":str(exc)}, sort_keys=True))
else:
    print(json.dumps({"status":"ok","args":args,"kwargs":kwargs}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def observe(py: Path, repo: Path) -> dict:
    p = subprocess.run([str(py), "-c", SNIPPET], cwd=repo, capture_output=True, text=True)
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    return json.loads(lines[-1]) if lines else {"status":"process_error","returncode":p.returncode,"stderr":p.stderr[-2000:]}


def replay(repo: Path, revision: str, root: Path) -> list[dict]:
    run(["git", "checkout", "--force", revision], cwd=repo)
    env = root / f"venv-{revision[:8]}"
    run([sys.executable, "-m", "venv", str(env)])
    py = env / "bin" / "python"
    run([str(py), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "--quiet", "-e", str(repo)])
    return [observe(py, repo) for _ in range(CONFIRMATION_REPEATS)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="v07-oa-4674-") as tmp:
        root = Path(tmp); repo = root / "openai-agents-python"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root); post = replay(repo, POST_FIX, root)
        verified = (
            all(x.get("status") == "ok" and x.get("kwargs", {}).get("opt") == 9 for x in pre)
            and all(x.get("status") == "error" and x.get("error_type") == "ModelBehaviorError" for x in post)
        )
        print(json.dumps({"source":"openai/openai-agents-python#4674","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__": raise SystemExit(main())
