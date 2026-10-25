"""Installed APIs must retain each audited option, result member and behavior test."""
import ast
import inspect
import importlib
import json
import typing
from pathlib import Path
import oxidize_pdf as pdf

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "docs/parity-contract.json").read_text(encoding="utf-8"))

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
    tree = ast.parse((ROOT / "tests/test_existing_document.py").read_text(encoding="utf-8"))
    test_names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert set(CONTRACT["required_tests"]) <= test_names

    for relative, required in CONTRACT.get("additional_tests", {}).items():
        tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
        names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        assert set(required) <= names


def test_signature_error_contract():
    schema = CONTRACT['signature_errors']
    assert set(typing.get_args(pdf.SignatureErrorCode)) == set(schema['codes'])
    assert {key: value.__name__ for key, value in typing.get_type_hints(pdf.SignatureErrorDetails).items()} == schema['fields']
    assert pdf.SignatureErrorDetails.__required_keys__ == frozenset()
    assert typing.get_type_hints(pdf.PdfSignatureError)['code'] == pdf.SignatureErrorCode
    assert typing.get_type_hints(pdf.PdfSignatureError)['details'] == pdf.SignatureErrorDetails
    for name, bases in schema['classes'].items():
        assert name in pdf.__all__
        cls = getattr(pdf, name)
        assert [base.__name__ for base in cls.__bases__] == bases
        assert issubclass(cls, pdf.PdfError)
