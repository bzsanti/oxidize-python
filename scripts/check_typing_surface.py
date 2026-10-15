#!/usr/bin/env python3
"""Inventory installed public exports/members against both shipped stubs.

This checks presence and callable parameter contracts, not return semantics or
Rust feature parity. Run after building the extension; optional native features
are checked when installed. Python-defined exports resolve to their typed source.
"""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SPECIAL = {"__init__", "__iter__", "__next__", "__enter__", "__exit__", "__len__", "__getitem__"}


def declarations(path: Path) -> dict[str, ast.AST]:
    result: dict[str, ast.AST] = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            result[node.name] = node
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            result[node.target.id] = node
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                result[alias.asname or alias.name] = node
    return result


def members(node: ast.ClassDef) -> dict[str, ast.AST]:
    result: dict[str, ast.AST] = {}
    for child in node.body:
        if isinstance(child, ast.FunctionDef):
            result[child.name] = child
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            result[child.target.id] = child
    return result


def parameter_errors(label: str, obj: object, node: ast.FunctionDef) -> list[str]:
    try:
        signature = inspect.signature(obj)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return []  # PyO3 exposes no signature for a few protocol slots.
    actual = {name: parameter.default is not inspect.Parameter.empty
              for name, parameter in signature.parameters.items() if name not in ("self", "cls")}
    args = node.args
    positional = args.posonlyargs + args.args
    defaults = [False] * (len(positional) - len(args.defaults)) + [True] * len(args.defaults)
    expected = {arg.arg: default for arg, default in zip(positional, defaults)
                if arg.arg not in ("self", "cls")}
    expected.update({arg.arg: default is not None for arg, default in zip(args.kwonlyargs, args.kw_defaults)})
    if list(actual.items()) != list(expected.items()):
        return [f"{label}: runtime parameters {actual} != stub {expected}"]
    return []


def inventory(package: ModuleType, native: ModuleType, stub_root: Path) -> tuple[dict[str, list[str]], list[str]]:
    public = declarations(stub_root / "__init__.pyi")
    extension = declarations(stub_root / "_oxidize_pdf.pyi")
    errors: list[str] = []
    optional_members = set() if hasattr(native, "AnalysisPipeline") else {
        ("Element", "class_label"), ("PdfReader", "rag_chunks_with_pipeline")
    }
    report: dict[str, list[str]] = {}
    for name in package.__all__:
        node = public.get(name)
        if not isinstance(node, ast.ImportFrom):
            errors.append(f"Public export missing: {name}")
            continue
        if node.module == "oxidize_pdf._oxidize_pdf":
            alias = next(a for a in node.names if (a.asname or a.name) == name)
            if alias.name not in extension:
                errors.append(f"Native declaration missing for {name}: {alias.name}")
            elif not hasattr(native, alias.name):
                errors.append(f"Native export missing at runtime: {alias.name}")
            elif getattr(package, name) is not getattr(native, alias.name):
                errors.append(f"Public alias points to a different object: {name}")
        # Python-defined exceptions, unions and TypedDicts have typed .py sources.
        elif node.module not in ("oxidize_pdf.signature_errors", "oxidize_pdf.parse_events"):
            errors.append(f"Unreviewed Python export source: {name}: {node.module}")
    for name in sorted(n for n in vars(native) if not n.startswith("_") or n == "__version__"):
        obj = getattr(native, name)
        node = extension.get(name)
        report[name] = []
        if node is None:
            errors.append(f"Native declaration missing: {name}")
        elif isinstance(node, ast.ClassDef) and inspect.isclass(obj):
            declared = members(node)
            for key in declared:
                if key != "__init__" and (name, key) not in optional_members and not hasattr(obj, key):
                    errors.append(f"Declared member absent at runtime: {name}.{key}")
            exposed = {key for key in vars(obj) if not key.startswith("_") or key in SPECIAL}
            if "__new__" in vars(obj):
                exposed.add("__init__")
            report[name] = sorted(exposed)
            for key in sorted(exposed):
                member = declared.get(key)
                if member is None:
                    errors.append(f"Member missing: {name}.{key}")
                elif isinstance(member, ast.FunctionDef) and callable(getattr(obj, key)):
                    errors.extend(parameter_errors(f"{name}.{key}", obj if key == "__init__" else getattr(obj, key), member))
        elif isinstance(node, ast.FunctionDef):
            errors.extend(parameter_errors(name, obj, node))
    return report, errors


def main() -> int:
    import oxidize_pdf
    import oxidize_pdf._oxidize_pdf as native

    report, errors = inventory(oxidize_pdf, native, ROOT / "python/oxidize_pdf")
    if "--json" in sys.argv:
        print(json.dumps({"exports": report, "errors": errors}, indent=2, sort_keys=True))
    else:
        print(f"Inventoried {len(report)} native exports, {sum(map(len, report.values()))} members, "
              f"{len(oxidize_pdf.__all__)} public exports")
        for error in errors:
            print(error, file=sys.stderr)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
