"""Installed APIs must retain each audited option, result member and behavior test."""
import ast
import inspect
import importlib
import json
from pathlib import Path
import oxidize_pdf as pdf

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "docs/parity-contract.json").read_text())

def test_audited_parity_contract():
    for relative, records in CONTRACT.get("typed_dicts", {}).items():
        module = importlib.import_module(relative.removeprefix('python/').removesuffix('.py').replace('/', '.'))
        for name, fields in records.items():
            assert getattr(module, name).__required_keys__ == set(fields)
    for path, parameters in CONTRACT["callables"].items():
        parts = path.split(".")
        assert parts[0] in pdf.__all__
        member = pdf
        for part in parts:
            member = getattr(member, part)
        assert list(inspect.signature(member).parameters) == parameters, path
    for name, properties in CONTRACT["properties"].items():
        assert name in pdf.__all__
        cls = getattr(pdf, name)
        for prop in properties:
            assert hasattr(cls, prop), f"{name}.{prop}"
    tree = ast.parse((ROOT / "tests/test_existing_document.py").read_text())
    test_names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert set(CONTRACT["required_tests"]) <= test_names

    for relative, required in CONTRACT.get("additional_tests", {}).items():
        tree = ast.parse((ROOT / relative).read_text())
        names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        assert set(required) <= names
