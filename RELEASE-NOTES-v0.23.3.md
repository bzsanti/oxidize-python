# oxidize-python 0.23.3

Updates the exact registry dependency to oxidize-pdf 5.5.5. Inherits fixes for minimum patched trust-store and key-distrust dependency versions, encrypted object streams, text spacing and compact lines, and page generation references during signature and document-timestamp preparation.

Text chunks now use page fonts and ToUnicode mappings, preserving content order, coordinates, artifacts and figure text.

Migrates macOS wheel builds to macos-15. The 0.23.2 tag was not published to PyPI because GitHub cancelled the macos-14 jobs during the scheduled runner retirement brownout.
