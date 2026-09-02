from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/openai/openai-agents-python.git"
PRE_FIX = "3603dc92c90d0d9aebf382e6c0e7dbc6b22d430a"
POST_FIX = "e773b15488c491d907d42756d91e470f280a3d7e"
CONFIRMATION_REPEATS = 3

SNIPPET = r'''
import json
from agents.function_schema import function_schema


def func(*args: tuple[int, ...]) -> int:
    return sum(sum(arg) for arg in args)

try:
    fs = function_schema(func, use_docstring_info=False)
    args_schema = fs.params_json_schema.get("properties", {}).get("args", {})
    parsed_nested = None
    nested_error = None
    try:
        parsed = fs.params_pydantic_model.model_validate({"args": [[1, 2], [3]]})
        call_args, call_kwargs = fs.to_call_args(parsed)
        parsed_nested = func(*call_args, **call_kwargs)
    except Exception as exc:
        nested_error = type(exc).__name__
    print(json.dumps({
        "status": "ok",
        "args_schema": args_schema,
        "nested_result": parsed_nested,
        "nested_error": nested_error,
    }, sort_keys=True))
except Exception as exc:
    print(json.dumps({"status": "error", "error_type": type(exc).__name__, "message": str(exc)}))
'''


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def _observe(python: Path, repo: Path) -> dict:
    completed = subprocess.run(
        [str(python), "-c", SNIPPET],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
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


def _schema_signature(observation: dict) -> tuple[str | None, str | None, str | None]:
    schema = observation.get("args_schema", {})
    items = schema.get("items", {}) if isinstance(schema, dict) else {}
    inner = items.get("items", {}) if isinstance(items, dict) else {}
    return schema.get("type"), items.get("type"), inner.get("type")


def _pre_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and _schema_signature(observation) == ("array", "integer", None)
        and observation.get("nested_result") is None
        and observation.get("nested_error") is not None
    )


def _post_expected(observation: dict) -> bool:
    return (
        observation.get("status") == "ok"
        and _schema_signature(observation) == ("array", "array", "integer")
        and observation.get("nested_result") == 6
        and observation.get("nested_error") is None
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mechanism-diff-c001-") as tmp:
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
            "case_id": "C001",
            "source": "openai/openai-agents-python#4655",
            "repository": "openai/openai-agents-python",
            "pre_fix_revision": PRE_FIX,
            "post_fix_revision": POST_FIX,
            "confirmation_repeats": CONFIRMATION_REPEATS,
            "pre_fix_runs": pre_runs,
            "post_fix_runs": post_runs,
            "replay_verified": verified,
        }, indent=2, sort_keys=True))
        return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
