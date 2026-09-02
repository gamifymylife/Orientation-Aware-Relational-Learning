"""Frozen generic apparatus for OARL v0.7 external Track R.

This module deliberately has no knowledge of repositories, pull requests, changed files,
post-fix regression tests, historical assertions, or semantic bug labels.  It turns a
pre-fix Python test source into a bounded set of single-site input mutations and exposes
only anonymized structural metadata to acquisition policies.

The confirmatory protocol is documented in
``evidence/v07/external/AMENDMENT_002_TRACK_R_PROBE_LANGUAGE.md``.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

MAX_CANDIDATES = 512
DEFAULT_STUDY_SEED = 20260826

# Calls whose literal arguments are ordinarily part of the test oracle/control plane,
# rather than inputs to the system under test.  They are excluded mechanically.
_ORACLE_LEAVES = {
    "approx",
    "fail",
    "raises",
    "skip",
    "skipif",
    "warns",
    "xfail",
    "parametrize",
}

_PATH_RE = re.compile(r"(?:[A-Za-z]:)?(?:[/\\][^\s:/\\]+)+")
_HEX_RE = re.compile(r"\b[0-9a-fA-F]{7,64}\b")
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
_WS_RE = re.compile(r"\s+")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _call_leaf(call: ast.Call) -> str | None:
    fn = call.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return None


def _is_test_function(node: ast.AST, class_name: str | None = None) -> bool:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    if node.name.startswith("test_"):
        return True
    return bool(class_name and class_name.startswith("Test") and node.name.startswith("test"))


def _iter_test_functions(tree: ast.Module) -> Iterable[ast.FunctionDef | ast.AsyncFunctionDef]:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_test_function(node):
            yield node
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for child in node.body:
                if _is_test_function(child, node.name):
                    yield child


class _StructuralNormalizer(ast.NodeTransformer):
    """Remove semantic names/literal values while preserving executable shape."""

    def visit_Name(self, node: ast.Name) -> ast.AST:  # noqa: N802
        return ast.copy_location(ast.Name(id="N", ctx=node.ctx), node)

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:  # noqa: N802
        node = self.generic_visit(node)
        assert isinstance(node, ast.Attribute)
        node.attr = "A"
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:  # noqa: N802
        node.arg = "ARG"
        node.annotation = None
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:  # noqa: N802
        value = node.value
        if value is None:
            replacement: Any = None
        elif isinstance(value, bool):
            replacement = False
        elif isinstance(value, int):
            replacement = 0
        elif isinstance(value, float):
            replacement = 0.0
        elif isinstance(value, str):
            replacement = "S"
        elif isinstance(value, bytes):
            replacement = b"B"
        else:
            replacement = type(value).__name__
        return ast.copy_location(ast.Constant(value=replacement), node)


def structural_hash(node: ast.AST) -> str:
    normalized = _StructuralNormalizer().visit(copy.deepcopy(node))
    ast.fix_missing_locations(normalized)
    return _sha256_text(ast.dump(normalized, include_attributes=False))


def _fixture_shape_hash(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = fn.args
    shape = {
        "posonly": len(args.posonlyargs),
        "positional": len(args.args),
        "kwonly": len(args.kwonlyargs),
        "vararg": args.vararg is not None,
        "kwarg": args.kwarg is not None,
        "defaults": len(args.defaults),
        "kw_defaults": sum(value is not None for value in args.kw_defaults),
    }
    return _sha256_text(_canonical_json(shape))


def _value_category(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant):
        v = node.value
        if isinstance(v, bool):
            return "bool"
        if isinstance(v, int):
            return "int"
        if isinstance(v, float) and math.isfinite(v):
            return "float"
        if isinstance(v, str):
            return "str"
        return None
    if isinstance(node, ast.List):
        return "list"
    if isinstance(node, ast.Tuple):
        return "tuple"
    if isinstance(node, ast.Set):
        return "set"
    return None


def _replacement_nodes(node: ast.AST) -> list[tuple[str, ast.AST]]:
    """Return deterministic, type-compatible single-site replacements."""
    out: list[tuple[str, ast.AST]] = []
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool):
            out.append(("bool_flip", ast.Constant(not value)))
        elif isinstance(value, int):
            values = [-1, 0, 1, value - 1, value + 1]
            for new in values:
                if new != value:
                    out.append(("int_boundary", ast.Constant(new)))
        elif isinstance(value, float) and math.isfinite(value):
            values = [-1.0, 0.0, 1.0, value / 2.0, value * 2.0]
            for new in values:
                if math.isfinite(new) and new != value:
                    out.append(("float_boundary", ast.Constant(new)))
        elif isinstance(value, str):
            for new in ("", "x"):
                if new != value:
                    out.append(("str_boundary", ast.Constant(new)))
    elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        constructor = type(node)
        elements = list(node.elts)
        variants: list[tuple[str, list[ast.expr]]] = [("container_empty", [])]
        if elements:
            variants.append(("container_shrink", elements[:-1]))
            variants.append(("container_expand", elements + [copy.deepcopy(elements[0])]))
        seen: set[str] = set()
        for family, elts in variants:
            replacement = constructor(elts=[copy.deepcopy(x) for x in elts], ctx=ast.Load())
            key = ast.dump(replacement, include_attributes=False)
            if key not in seen and key != ast.dump(node, include_attributes=False):
                seen.add(key)
                out.append((family, replacement))
    # Stable de-duplication by rendered replacement rather than Python object identity.
    unique: dict[tuple[str, str], ast.AST] = {}
    for family, replacement in out:
        ast.fix_missing_locations(replacement)
        unique[(family, ast.unparse(replacement))] = replacement
    return [(family, replacement) for (family, _), replacement in sorted(unique.items())]


@dataclass(frozen=True)
class MutationCandidate:
    candidate_id: str
    operator_family: str
    value_category: str
    call_shape: str
    fixture_shape: str
    test_structure: str
    site_token: str
    policy_hash: str
    source_hash: str
    mutated_source: str

    def policy_view(self) -> dict[str, str]:
        """The only static candidate metadata acquisition policies may consume."""
        return {
            "candidate_id": self.candidate_id,
            "operator_family": self.operator_family,
            "value_category": self.value_category,
            "call_shape": self.call_shape,
            "fixture_shape": self.fixture_shape,
            "test_structure": self.test_structure,
            "site_token": self.site_token,
            "policy_hash": self.policy_hash,
        }


@dataclass(frozen=True)
class RelationGraph:
    candidate_ids: tuple[str, ...]
    edges: tuple[tuple[str, str, str], ...]

    def neighbours(self, candidate_id: str) -> tuple[tuple[str, str], ...]:
        rows: list[tuple[str, str]] = []
        for left, right, relation in self.edges:
            if left == candidate_id:
                rows.append((right, relation))
            elif right == candidate_id:
                rows.append((left, relation))
        return tuple(sorted(rows))


def _direct_mutation_sites(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[tuple[ast.Call, str, int | str, ast.AST]]:
    """Collect direct call arguments while excluding assertion/oracle subtrees."""
    sites: list[tuple[ast.Call, str, int | str, ast.AST]] = []

    def visit(node: ast.AST, blocked: bool = False) -> None:
        if isinstance(node, ast.Assert):
            return
        if isinstance(node, ast.Call):
            leaf = _call_leaf(node)
            oracle = bool(leaf and leaf.lower() in _ORACLE_LEAVES)
            if not blocked and not oracle:
                for index, arg in enumerate(node.args):
                    if _value_category(arg) is not None:
                        sites.append((node, "arg", index, arg))
                for kw in node.keywords:
                    if kw.arg is not None and _value_category(kw.value) is not None:
                        sites.append((node, "kw", kw.arg, kw.value))
            # Nested calls receive their own direct-argument treatment unless this call is oracle.
            for child in ast.iter_child_nodes(node):
                visit(child, blocked or oracle)
            return
        for child in ast.iter_child_nodes(node):
            visit(child, blocked)

    visit(fn)
    return sites


def _replace_target(module: ast.Module, lineno: int, col: int, kind: str, key: int | str, replacement: ast.AST) -> bool:
    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node, "lineno", None) != lineno or getattr(node, "col_offset", None) != col:
            continue
        if kind == "arg" and isinstance(key, int) and key < len(node.args):
            node.args[key] = copy.deepcopy(replacement)
            return True
        if kind == "kw" and isinstance(key, str):
            for kw in node.keywords:
                if kw.arg == key:
                    kw.value = copy.deepcopy(replacement)
                    return True
    return False


def generate_candidates(source: str, *, source_token: str = "pre_fix_test", max_candidates: int = MAX_CANDIDATES) -> list[MutationCandidate]:
    """Generate the frozen, bounded pre-fix-only mutation language for one test file."""
    if max_candidates < 1:
        raise ValueError("max_candidates must be positive")
    tree = ast.parse(source)
    source_hash = _sha256_text(source)
    candidates: list[MutationCandidate] = []
    rendered_seen: set[str] = set()

    for fn in _iter_test_functions(tree):
        fixture_shape = _fixture_shape_hash(fn)
        test_structure = structural_hash(fn)
        for call, kind, key, target in _direct_mutation_sites(fn):
            category = _value_category(target)
            if category is None:
                continue
            call_shape = structural_hash(call)
            site_material = {
                "source_token": source_token,
                "function_shape": test_structure,
                "call_shape": call_shape,
                "line": int(getattr(call, "lineno", 0)),
                "column": int(getattr(call, "col_offset", 0)),
                "kind": kind,
                "key": str(key),
            }
            site_token = _sha256_text(_canonical_json(site_material))[:24]
            for operator_family, replacement in _replacement_nodes(target):
                mutant_tree = copy.deepcopy(tree)
                changed = _replace_target(
                    mutant_tree,
                    int(getattr(call, "lineno", 0)),
                    int(getattr(call, "col_offset", 0)),
                    kind,
                    key,
                    replacement,
                )
                if not changed:
                    continue
                ast.fix_missing_locations(mutant_tree)
                rendered = ast.unparse(mutant_tree) + "\n"
                rendered_hash = _sha256_text(rendered)
                if rendered_hash in rendered_seen or rendered_hash == source_hash:
                    continue
                rendered_seen.add(rendered_hash)
                policy_core = {
                    "operator_family": operator_family,
                    "value_category": category,
                    "call_shape": call_shape,
                    "fixture_shape": fixture_shape,
                    "test_structure": test_structure,
                    "site_token": site_token,
                }
                policy_hash = _sha256_text(_canonical_json(policy_core))
                candidate_id = "r-" + _sha256_text(policy_hash + ":" + rendered_hash)[:20]
                candidates.append(
                    MutationCandidate(
                        candidate_id=candidate_id,
                        operator_family=operator_family,
                        value_category=category,
                        call_shape=call_shape,
                        fixture_shape=fixture_shape,
                        test_structure=test_structure,
                        site_token=site_token,
                        policy_hash=policy_hash,
                        source_hash=rendered_hash,
                        mutated_source=rendered,
                    )
                )

    # Frozen fixed ordering: hash of canonical policy-visible representation.
    candidates.sort(key=lambda c: (_sha256_text(_canonical_json(c.policy_view())), c.candidate_id))
    return candidates[:max_candidates]


def candidate_manifest(candidates: Sequence[MutationCandidate]) -> dict[str, Any]:
    views = [candidate.policy_view() for candidate in candidates]
    return {
        "schema_version": 1,
        "generator": "oarl-v07-track-r-pre-fix-single-site-v1",
        "candidate_count": len(views),
        "candidates": views,
        "manifest_sha256": _sha256_text(_canonical_json(views)),
    }


def build_relation_graph(candidates: Sequence[MutationCandidate]) -> RelationGraph:
    """Create only mechanically justified, policy-visible relation edges."""
    relation_fields = {
        "same_operator_family": "operator_family",
        "same_value_category": "value_category",
        "same_call_shape": "call_shape",
        "same_fixture_shape": "fixture_shape",
        "same_test_structure": "test_structure",
    }
    edges: set[tuple[str, str, str]] = set()
    for relation, field in relation_fields.items():
        groups: dict[str, list[str]] = defaultdict(list)
        for candidate in candidates:
            groups[str(getattr(candidate, field))].append(candidate.candidate_id)
        for ids in groups.values():
            ids = sorted(ids)
            for i, left in enumerate(ids):
                for right in ids[i + 1 :]:
                    edges.add((left, right, relation))
    return RelationGraph(
        candidate_ids=tuple(sorted(candidate.candidate_id for candidate in candidates)),
        edges=tuple(sorted(edges)),
    )


def scrambled_relation_graph(graph: RelationGraph, *, seed: int = DEFAULT_STUDY_SEED) -> RelationGraph:
    """Permute endpoint labels while preserving the relation multigraph exactly.

    Individual candidate metadata and candidate ordering are untouched; only which
    candidate occupies each relational position changes.
    """
    import random

    ids = list(graph.candidate_ids)
    shuffled = list(ids)
    random.Random(seed).shuffle(shuffled)
    permutation = dict(zip(ids, shuffled, strict=True))
    edges = []
    for left, right, relation in graph.edges:
        a, b = sorted((permutation[left], permutation[right]))
        if a != b:
            edges.append((a, b, relation))
    return RelationGraph(candidate_ids=graph.candidate_ids, edges=tuple(sorted(set(edges))))


def _normalize_text(text: str, *, limit: int = 512) -> str:
    text = _PATH_RE.sub("<PATH>", text or "")
    text = _HEX_RE.sub("<HEX>", text)
    text = _NUMBER_RE.sub("<N>", text)
    text = _WS_RE.sub(" ", text).strip()
    return text[:limit]


def normalize_observation(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize one executable result without repository/semantic labels."""
    returncode = raw.get("returncode", raw.get("exit_code"))
    outcome = raw.get("outcome")
    if outcome is None:
        outcome = "pass" if returncode == 0 else "fail"
    exception = raw.get("exception_class") or raw.get("exception")
    if exception is not None:
        exception = str(exception).split(".")[-1].split(":")[0]
    warnings = raw.get("warning_count", raw.get("warnings", 0))
    if isinstance(warnings, Sequence) and not isinstance(warnings, (str, bytes, bytearray)):
        warnings = len(warnings)
    try:
        warning_count = int(warnings or 0)
    except (TypeError, ValueError):
        warning_count = 0
    runtime = raw.get("runtime_seconds")
    try:
        runtime_f = max(0.0, float(runtime))
    except (TypeError, ValueError):
        runtime_f = 0.0
    if runtime_f < 0.1:
        runtime_bucket = "lt_0.1"
    elif runtime_f < 1.0:
        runtime_bucket = "lt_1"
    elif runtime_f < 10.0:
        runtime_bucket = "lt_10"
    else:
        runtime_bucket = "ge_10"
    return {
        "outcome": str(outcome).lower(),
        "exit_status": returncode,
        "exception_class": exception,
        "warning_count": warning_count,
        "stdout_shape": _sha256_text(_normalize_text(str(raw.get("stdout", ""))))[:16],
        "stderr_shape": _sha256_text(_normalize_text(str(raw.get("stderr", ""))))[:16],
        "trace_shape": _sha256_text(_normalize_text(str(raw.get("traceback", raw.get("trace", "")))))[:16],
        "runtime_bucket": runtime_bucket,
    }


def orientation_projection(observation: Mapping[str, Any]) -> dict[str, Any]:
    """Frozen atomic + tuple projection family for relation-aware acquisition."""
    keys = (
        "outcome",
        "exit_status",
        "exception_class",
        "warning_count",
        "stdout_shape",
        "stderr_shape",
        "trace_shape",
        "runtime_bucket",
    )
    atomic = {key: observation.get(key) for key in keys}
    tuples = {
        "outcome_exception": (atomic["outcome"], atomic["exception_class"]),
        "io_shape": (atomic["stdout_shape"], atomic["stderr_shape"]),
        "status_runtime": (atomic["exit_status"], atomic["runtime_bucket"]),
    }
    return {"atomic": atomic, "tuples": tuples}


def behavioural_distance(a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
    """Normalized Hamming distance over the frozen orientation family, in [0,1]."""
    pa = orientation_projection(a)
    pb = orientation_projection(b)
    av = list(pa["atomic"].values()) + list(pa["tuples"].values())
    bv = list(pb["atomic"].values()) + list(pb["tuples"].values())
    if not av:
        return 0.0
    return sum(x != y for x, y in zip(av, bv, strict=True)) / len(av)


def relation_counts(graph: RelationGraph) -> dict[str, int]:
    return dict(sorted(Counter(relation for _, _, relation in graph.edges).items()))
