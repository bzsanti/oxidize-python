# Core 5.5.6 adoption

Python 0.23.4 pins the published oxidize-pdf 5.5.6 crate. Incremental signing now enforces signed field Lock/P restrictions from earlier revisions. The core can prepare dedicated invisible timestamps under P1, but this Python binding does not expose that API. Existing signatures and chunking APIs are preserved.

The core also fixes semantic token budgets. This dependency adoption does not add a Python exact-token-counter API or establish full parity (#244, core #710). Python's current hybrid pipeline retains its word-proxy default.

Validation covers existing binding behavior, signed-field permission controls and the published-package consumer. See the delivery evidence for actual results; release availability is verified after publication.
