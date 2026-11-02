# oxidize-pdf Python 0.23.4

Adopts Rust core 5.5.6 with corrected signed-field Lock/P enforcement. Attempts to add signatures contrary to an earlier signed policy now fail. The core also permits dedicated invisible document timestamps under P1; that API is not exposed by this Python binding. Public Python APIs are unchanged.

Core semantic chunk-budget fixes are included in the dependency; this release does not introduce exact token counting to Python. Full functional parity remains tracked in #244 and core #710.
