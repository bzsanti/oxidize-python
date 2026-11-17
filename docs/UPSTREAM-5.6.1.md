# Core 5.6.1 in bridge 0.24.1

The exact registry dependency is `oxidize-pdf =5.6.1`. `PdfReader.from_bytes`
with `ParseOptions.strict()` resolves indirect stream lengths when reading page
content streams. Invalid lengths and references remain errors; failed reads
must not cache a successful result. The core also allocates modern object-stream
identifiers from the document's object namespace.

`tests/test_core561.py` checks exact decoded content bytes, marker-like payloads,
empty streams, invalid lengths, references and repeated failed reads through the
public reader. Publication and clean installed-package checks are tracked in #317.

The extraction controls and compatibility limits described for [5.6.0](UPSTREAM-5.6.0.md)
remain applicable. This update adds no Python API and does not claim full core parity.
