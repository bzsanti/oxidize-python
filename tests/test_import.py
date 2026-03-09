"""Test that the oxidize_pdf module can be imported and has basic attributes."""


def test_module_imports():
    import oxidize_pdf

    assert oxidize_pdf is not None


def test_has_version():
    import oxidize_pdf

    assert hasattr(oxidize_pdf, "__version__")
    assert isinstance(oxidize_pdf.__version__, str)
    assert len(oxidize_pdf.__version__) > 0


def test_version_is_semver():
    import oxidize_pdf

    parts = oxidize_pdf.__version__.split(".")
    assert len(parts) >= 2
    assert all(part.isdigit() for part in parts)
