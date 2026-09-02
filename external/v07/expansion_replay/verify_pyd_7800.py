from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/pydantic/pydantic-ai.git"
PRE_FIX = "fad54a9ff1c648cc63a1031652912b062d5644c6"
POST_FIX = "83271652e4691e68e13f32972855c1e623141a0a"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from pydantic_ai.models.test import _JsonSchemaTestData
schema = {"type": "number", "minimum": 0, "exclusiveMaximum": 1}
try:
    value = _JsonSchemaTestData(schema, seed=0).generate()
except BaseException as exc:
    print(json.dumps({"status":"error","error_type":type(exc).__name__,"message":str(exc)}, sort_keys=True))
else:
    print(json.dumps({"status":"ok","value":value}, sort_keys=True))
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
    run([str(py), "-m", "pip", "install", "--quiet", "-e", str(repo / "pydantic_graph"), "-e", str(repo / "pydantic_ai_slim")])
    return [observe(py, repo) for _ in range(CONFIRMATION_REPEATS)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="v07-pyd-7800-") as tmp:
        root = Path(tmp); repo = root / "pydantic-ai"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root); post = replay(repo, POST_FIX, root)
        verified = all(x.get("status") == "error" for x in pre) and all(x == {"status":"ok","value":0.0} for x in post)
        print(json.dumps({"source":"pydantic/pydantic-ai#7800","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__": raise SystemExit(main())
