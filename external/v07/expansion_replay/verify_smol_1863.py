from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/huggingface/smolagents.git"
PRE_FIX = "bf94940b1a78d4acbc4905c5bc78ee131f35a9ba"
POST_FIX = "2ae00fb092d1b0e7d74de06e738dd48d04a8b2c2"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
import tempfile
from pathlib import Path
from smolagents.agents import MultiStepAgent

class ProbeAgent(MultiStepAgent):
    @classmethod
    def from_dict(cls, agent_dict, **kwargs):
        return agent_dict

agent_dict = {
    "model": {"class": "HfApiModel", "data": {}},
    "managed_agents": {},
    "tools": [],
}
with tempfile.TemporaryDirectory() as tmp:
    folder = Path(tmp)
    (folder / "agent.json").write_text(json.dumps(agent_dict))
    try:
        result = ProbeAgent.from_folder(folder)
    except BaseException as exc:
        print(json.dumps({"status":"error","error_type":type(exc).__name__,"message":str(exc)}, sort_keys=True))
    else:
        print(json.dumps({"status":"ok","model_class":result["model"]["class"]}, sort_keys=True))
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
    with tempfile.TemporaryDirectory(prefix="v07-smol-1863-") as tmp:
        root = Path(tmp); repo = root / "smolagents"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root); post = replay(repo, POST_FIX, root)
        verified = (
            all(x == {"status":"ok","model_class":"HfApiModel"} for x in pre)
            and all(x == {"status":"ok","model_class":"InferenceClientModel"} for x in post)
        )
        print(json.dumps({"source":"huggingface/smolagents#1863","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__": raise SystemExit(main())
