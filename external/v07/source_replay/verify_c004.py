from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/openai/openai-agents-python.git"
PRE_FIX = "5f9f4f09c3fe840b5a4c09bdbbf6f0b1239bf0ec"
POST_FIX = "1df6e81474a439d4fff8eac227743cfb3f5d2d6d"
CONFIRMATION_REPEATS = 3
SENSITIVE_PROMPT = "customer account vocabulary"

SNIPPET = rf'''
import json
from unittest.mock import AsyncMock, MagicMock, patch

from agents.voice import OpenAISTTTranscriptionSession, StreamedAudioInput, STTModelSettings

PROMPT = {SENSITIVE_PROMPT!r}

session = OpenAISTTTranscriptionSession(
    input=StreamedAudioInput(),
    client=AsyncMock(api_key="FAKE_KEY"),
    model="whisper-1",
    settings=STTModelSettings(prompt=PROMPT),
    trace_include_sensitive_data=False,
    trace_include_sensitive_audio_data=False,
)
span = MagicMock()
with patch(
    "agents.voice.models.openai_stt.transcription_span",
    return_value=span,
) as create_span:
    session._start_turn()

request_config = session._get_transcription_config()
print(json.dumps({{
    "status": "ok",
    "trace_prompt": create_span.call_args.kwargs["model_config"]["prompt"],
    "request_prompt": request_config["prompt"],
}}, sort_keys=True))
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
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("revision produced no replay output")
    return json.loads(lines[-1])


def replay(repo: Path, revision: str, work: Path) -> list[dict]:
    run(["git", "checkout", "--force", revision], cwd=repo)
    env = work / f"venv-{revision[:8]}"
    run([sys.executable, "-m", "venv", str(env)])
    python = env / "bin" / "python"
    run([str(python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
    run([str(python), "-m", "pip", "install", "--quiet", "-e", f"{repo}[voice]"])
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and observation.get("trace_prompt") == SENSITIVE_PROMPT
        and observation.get("request_prompt") == SENSITIVE_PROMPT
    )


def _post_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and observation.get("trace_prompt") is None
        and observation.get("request_prompt") == SENSITIVE_PROMPT
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c004-") as tmp:
        root = Path(tmp)
        repo = root / "openai-agents-python"
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
            "case_id": "C004",
            "source": "openai/openai-agents-python#4663",
            "repository": "openai/openai-agents-python",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "bounded_interface": "offline STT session trace construction with identical prompt/settings on both revisions",
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
