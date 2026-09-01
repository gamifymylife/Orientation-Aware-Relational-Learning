from __future__ import annotations

# Exact-revision eligibility replay for C005.
import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/openai/openai-agents-python.git"
PRE_FIX = "5f9f4f09c3fe840b5a4c09bdbbf6f0b1239bf0ec"
POST_FIX = "5c00f985323765cc23240e82138e71aecf86a59b"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import asyncio
import json

from agents import Agent, Runner, function_tool
from agents.guardrail import GuardrailFunctionOutput
from agents.items import TResponseInputItem
from agents.lifecycle import RunHooks
from agents.memory import Session
from agents.run import RunConfig
from agents.run_context import RunContextWrapper
from agents.run_state import RunState
from agents.testing import ScriptedModel
from agents.tool import Tool
from agents.tool_guardrails import (
    ToolGuardrailFunctionOutput,
    ToolInputGuardrailData,
    ToolOutputGuardrailData,
    tool_input_guardrail,
    tool_output_guardrail,
)
from tests.test_responses import get_function_tool_call
from tests.utils.simple_session import SimpleListSession


class ResumeWriteFailureSession(SimpleListSession):
    def __init__(self):
        super().__init__()
        self.fail_next = False

    async def add_items(self, items: list[TResponseInputItem]) -> None:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("session append failed")
        await super().add_items(items)


class CountingHooks(RunHooks):
    def __init__(self):
        self.starts = 0
        self.ends = 0

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.starts += 1

    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool: Tool, result: object) -> None:
        self.ends += 1


async def main():
    counters = {"effect": 0, "input": 0, "output": 0}

    @tool_input_guardrail
    async def record_input(_data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
        counters["input"] += 1
        return ToolGuardrailFunctionOutput.allow(output_info="input-checked")

    @tool_output_guardrail
    async def record_output(_data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
        counters["output"] += 1
        return ToolGuardrailFunctionOutput.allow(output_info="output-checked")

    @function_tool(
        needs_approval=True,
        tool_input_guardrails=[record_input],
        tool_output_guardrails=[record_output],
    )
    async def charge(amount: int) -> str:
        counters["effect"] += 1
        return f"receipt-{amount}"

    @function_tool(needs_approval=True)
    async def notify() -> str:
        raise AssertionError("unresolved approval must not execute")

    model = ScriptedModel([
        [
            get_function_tool_call("charge", '{"amount":7}', call_id="charge-1"),
            get_function_tool_call("notify", "{}", call_id="notify-1"),
        ],
    ])
    agent = Agent(name="payment", model=model, tools=[charge, notify])
    session: Session = ResumeWriteFailureSession()
    hooks = CountingHooks()
    config = RunConfig(tracing_disabled=True)

    paused = await Runner.run(agent, "charge 7 and notify", session=session, hooks=hooks, run_config=config)
    state: RunState = paused.to_state()
    charge_approval = next(
        item for item in state.get_interruptions() if item.raw_item.call_id == "charge-1"
    )
    state.approve(charge_approval)

    session.fail_next = True
    error = None
    try:
        await Runner.run(agent, state, session=session, hooks=hooks, run_config=config)
    except RuntimeError as exc:
        error = str(exc)

    input_results = getattr(state, "_tool_input_guardrail_results", [])
    output_results = getattr(state, "_tool_output_guardrail_results", [])
    print(json.dumps({
        "status": "ok",
        "error": error,
        "input_guardrail_results": len(input_results),
        "output_guardrail_results": len(output_results),
        "effect_count": counters["effect"],
        "input_guardrail_count": counters["input"],
        "output_guardrail_count": counters["output"],
        "hook_starts": hooks.starts,
        "hook_ends": hooks.ends,
        "model_calls": len(model.calls),
        "remaining_interruptions": [item.raw_item.call_id for item in state.get_interruptions()],
    }, sort_keys=True))


asyncio.run(main())
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
    run([str(python), "-m", "pip", "install", "--quiet", "-e", str(repo)])
    return [_observe(python, repo) for _ in range(CONFIRMATION_REPEATS)]


def _common_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and observation.get("error") == "session append failed"
        and observation.get("effect_count") == 1
        and observation.get("input_guardrail_count") == 1
        and observation.get("output_guardrail_count") == 1
        and observation.get("hook_starts") == 1
        and observation.get("hook_ends") == 1
        and observation.get("model_calls") == 1
        and observation.get("remaining_interruptions") == ["notify-1"]
    )


def _pre_expected(observation: dict) -> bool:
    return (
        _common_expected(observation)
        and observation.get("input_guardrail_results") == 0
        and observation.get("output_guardrail_results") == 0
    )


def _post_expected(observation: dict) -> bool:
    return (
        _common_expected(observation)
        and observation.get("input_guardrail_results") == 1
        and observation.get("output_guardrail_results") == 1
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c005-") as tmp:
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
            "case_id": "C005",
            "source": "openai/openai-agents-python#4654",
            "repository": "openai/openai-agents-python",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "bounded_interface": "public Runner recovery from an approved guarded tool when a client-managed Session append fails before commit",
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
