from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/pydantic/pydantic-ai.git"
PRE_FIX = "1844574c3788e37f266f4f5c89920b62dd24cdd3"
POST_FIX = "116cfda251a49efad3a2b60d90e8612ca2ce73ad"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from urllib.parse import urlsplit

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.realtime.openai import OpenAIRealtimeModel

provider = OpenAIProvider(api_key="sk-test", base_url="https://host.example/v1#frag")
model = OpenAIRealtimeModel("gpt-realtime", provider=provider)
url = model._webrtc_calls_url()
parsed = urlsplit(url)
print(json.dumps({
    "status": "ok",
    "url": url,
    "path": parsed.path,
    "fragment": parsed.fragment,
}, sort_keys=True))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def _observe(python: Path, repo: Path) -> dict:
    completed = subprocess.run(
        [str(python), "-c", SNIPPET],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "revision replay failed\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    for line in reversed(completed.stdout.splitlines()):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("status") == "ok":
            return value
    raise RuntimeError(f"revision produced no JSON replay output\nstdout:\n{completed.stdout}")


def replay(repo: Path, revision: str, work: Path) -> list[dict]:
    run(["git", "checkout", "--force", revision], cwd=repo)
    env = work / f"venv-{revision[:8]}"
    run([sys.executable, "-m", "venv", str(env)])
    python = env / "bin" / "python"
    run([str(python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--quiet",
            "-e",
            str(repo / "pydantic_graph"),
            "-e",
            str(repo / "pydantic_ai_slim") + "[openai-realtime]",
        ]
    )
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return observation == {
        "status": "ok",
        "url": "https://host.example/v1/#frag/realtime/calls",
        "path": "/v1/",
        "fragment": "frag/realtime/calls",
    }


def _post_expected(observation: dict) -> bool:
    return observation == {
        "status": "ok",
        "url": "https://host.example/v1/realtime/calls#frag",
        "path": "/v1/realtime/calls",
        "fragment": "frag",
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c007-") as tmp:
        root = Path(tmp)
        repo = root / "pydantic-ai"
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
            "case_id": "C007",
            "source": "pydantic/pydantic-ai#7412",
            "repository": "pydantic/pydantic-ai",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "bounded_interface": "OpenAIRealtimeModel WebRTC signaling URL construction with identical provider base URL containing a fragment",
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
