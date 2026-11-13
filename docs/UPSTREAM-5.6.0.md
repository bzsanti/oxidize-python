# Core 5.6.0 in bridge 0.24.0

This release pins the published `oxidize-pdf =5.6.0` crate. It adds three opt-in extraction controls: visual line ordering, fallback to explicit font encoding for incomplete ToUnicode maps, and annotation appearance text. All three default to false. Encoding fallback can recover characters absent from a map; it does not establish that a damaged PDF's original meaning has been recovered.

The default TJ spacing threshold is now 0.17, matching the core. Set it explicitly to 0.2 to retain the earlier sensitivity. This can change whitespace in extracted text.

Annotation appearance extraction preserves strict stream errors. Explicit bounded recovery reports annotation appearance stream object IDs; inspect diagnostics before accepting recovered text. Stream-byte and emitted-text budgets remain independent. Annotation text follows page content in ordinary extraction; visual ordering is separately opt-in.

This is an extraction increment, not a claim of full core API parity. Existing compatibility limits remain applicable. The regression fixtures in `core560` are assembled independently of the PDF library and exercise source/visual order, an incomplete font map, TJ spacing, and healthy/damaged annotation streams.
