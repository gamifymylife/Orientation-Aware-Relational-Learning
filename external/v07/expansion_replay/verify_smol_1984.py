from __future__ import annotations

import base64
import json
import pickle
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/huggingface/smolagents.git"
PRE_FIX = "b48889204ad50b6dce7546ae364eedc6ceb87d46"
POST_FIX = "7f21b7480e9510cbee57ec5cae8969646a1f17ed"
CONFIRMATION_REPEATS = 3
PAYLOAD = base64.b64encode(pickle.dumps({"status": "ok", "count": 2})).decode()

SNIPPET = rf'''
import json
from smolagents.remote_executors import RemotePythonExecutor
payload = {PAYLOAD!r}
try:
    value = RemotePythonExecutor._deserialize_final_answer(payload, allow_pickle=True)
except BaseException as exc:
    print(json.dumps({{"status":"error","error_type":type(exc).__name__,"message":str(exc)}}, sort_keys=True))
else:
    print(json.dumps({{"status":"ok","value":value}}, sort_keys=True))
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
    with tempfile.TemporaryDirectory(prefix="v07-smol-1984-") as tmp:
        root = Path(tmp); repo = root / "smolagents"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root); post = replay(repo, POST_FIX, root)
        verified = all(x.get("status") == "error" for x in pre) and all(x == {"status":"ok","value":{"status":"ok","count":2}} for x in post)
        print(json.dumps({"source":"huggingface/smolagents#1984","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__": raise SystemExit(main())
