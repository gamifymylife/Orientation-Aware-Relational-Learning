from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/crewAIInc/crewAI.git"
PRE_FIX = "56e0e85a8186abd2929c17fed22e54bbbc327778"
POST_FIX = "039f6ff5f60395334130844bbf955382a24a1058"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
try:
    from crewai.llms.providers.anthropic.completion import AnthropicCompletion
    llm = AnthropicCompletion()
    params = llm._prepare_completion_params(messages=[{"role":"user","content":"hi"}])
    print(json.dumps({"status":"ok","model":llm.model,"max_tokens":llm.max_tokens,"prepared_max_tokens":params.get("max_tokens")}, sort_keys=True))
except BaseException as exc:
    print(json.dumps({"status":"error","error_type":type(exc).__name__,"message":str(exc)}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def observe(py: Path, repo: Path) -> dict:
    p = subprocess.run([str(py), "-c", SNIPPET], cwd=repo, capture_output=True, text=True, env={**__import__('os').environ, "ANTHROPIC_API_KEY":"test-key"})
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    return json.loads(lines[-1]) if lines else {"status":"process_error","returncode":p.returncode,"stderr":p.stderr[-2000:]}


def replay(repo: Path, revision: str, root: Path) -> list[dict]:
    run(["git", "checkout", "--force", revision], cwd=repo)
    env = root / f"venv-{revision[:8]}"
    run([sys.executable, "-m", "venv", str(env)])
    py = env / "bin" / "python"
    run([str(py), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "--quiet", "-e", str(repo / "lib" / "crewai")])
    return [observe(py, repo) for _ in range(CONFIRMATION_REPEATS)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="v07-crew-7077-") as tmp:
        root = Path(tmp); repo = root / "crewai"
        run(["git", "clone", "--quiet", "--filter=blob:none", REPOSITORY, str(repo)])
        pre = replay(repo, PRE_FIX, root); post = replay(repo, POST_FIX, root)
        verified = (
            all(x.get("status") == "ok" and x.get("max_tokens") == 4096 and x.get("prepared_max_tokens") == 4096 for x in pre)
            and all(x.get("status") == "ok" and x.get("max_tokens", 0) >= 32000 and x.get("prepared_max_tokens", 0) >= 32000 for x in post)
        )
        print(json.dumps({"source":"crewAIInc/crewAI#7077","pre_fix_revision":PRE_FIX,"post_fix_revision":POST_FIX,"pre_fix_runs":pre,"post_fix_runs":post,"replay_verified":verified}, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__": raise SystemExit(main())
