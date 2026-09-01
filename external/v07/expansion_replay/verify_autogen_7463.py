from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/microsoft/autogen.git"
PRE_FIX = "b0477309d2a0baf489aa256646e41e513ab3bfe8"
POST_FIX = "8544314fa6cc9f906c3ec2395927f5404ffbb5eb"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from autogen_core import ComponentModel
from autogen_core._component_config import ComponentLoader

bad_model = ComponentModel(provider="os.path.join", config={})
try:
    ComponentLoader.load_component(bad_model, object)
except BaseException as exc:
    print(json.dumps({"status":"error","error_type":type(exc).__name__,"message":str(exc)}, sort_keys=True))
else:
    print(json.dumps({"status":"ok"}, sort_keys=True))
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
    run([str(py), "-m", "pip", "install", "--quiet", "-e", str(repo / "python" / "packages" / "autogen-core")])
    return [observe(py, repo) for _ in range(CONFIRMATION_REPEATS)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="v07-autogen-7463-") as tmp:
        root = Path(tmp); repo = root / "autogen"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root); post = replay(repo, POST_FIX, root)
        verified = (
            all(x.get("status") == "error" and "not in a trusted namespace" not in x.get("message", "") for x in pre)
            and all(x.get("status") == "error" and "not in a trusted namespace" in x.get("message", "") for x in post)
        )
        print(json.dumps({"source":"microsoft/autogen#7463","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__": raise SystemExit(main())
