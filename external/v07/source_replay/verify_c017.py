from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/crewAIInc/crewAI.git"
PRE_FIX = "500ebc7a68b4f56eddf7fda6074375bb2b6cdc51"
POST_FIX = "c1998259c0a827410425c402cef0877af6a31dcd"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from typing import Any

from crewai import Agent
from crewai.llms.base_llm import BaseLLM


class Recorder(BaseLLM):
    def __init__(self) -> None:
        super().__init__(model="recorder")
        object.__setattr__(self, "seen", [])

    def call(self, messages: Any, **kwargs: Any) -> str:
        self.seen.append(list(messages) if isinstance(messages, list) else messages)
        return "ok"

    async def acall(self, messages: Any, **kwargs: Any) -> str:
        return self.call(messages, **kwargs)

    def supports_function_calling(self) -> bool:
        return False

    def supports_stop_words(self) -> bool:
        return False

    def get_context_window_size(self) -> int:
        return 8192


conversation = [
    {"role": "user", "content": "my order id is 42"},
    {"role": "assistant", "content": "thanks, checking"},
    {"role": "user", "content": "where is it?"},
]
llm = Recorder()
Agent(role="Support", goal="help", backstory="b", llm=llm).kickoff(conversation)
seen = llm.seen[0]
print(json.dumps({
    "status": "ok",
    "roles": [message["role"] for message in seen],
    "contents": [str(message.get("content")) for message in seen],
    "provider_message_count": len(seen),
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
    run([str(python), "-m", "pip", "install", "--quiet", "-e", str(repo / "lib" / "crewai")])
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _pre_expected(observation: dict) -> bool:
    contents = observation.get("contents", [])
    return (
        observation.get("status") == "ok"
        and observation.get("roles") == ["system", "user"]
        and observation.get("provider_message_count") == 2
        and any("my order id is 42" in content and "thanks, checking" in content and "where is it?" in content for content in contents)
    )


def _post_expected(observation: dict) -> bool:
    contents = observation.get("contents", [])
    return (
        observation.get("status") == "ok"
        and observation.get("roles") == ["system", "user", "assistant", "user"]
        and observation.get("provider_message_count") == 4
        and "my order id is 42" in contents[1]
        and contents[2] == "thanks, checking"
        and "where is it?" in contents[3]
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c017-") as tmp:
        root = Path(tmp)
        repo = root / "crewai"
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
            "case_id": "C017",
            "source": "crewAIInc/crewAI#7065",
            "repository": "crewAIInc/crewAI",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "bounded_interface": "public Agent.kickoff with the same three-message conversation and a local recording BaseLLM provider",
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
