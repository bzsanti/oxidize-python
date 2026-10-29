# Core 5.5.4 adoption review

Exact registry artifact verified against index checksum and release commit; see registry-identity.json. No path overrides. Core and certificate dependency corrections preserve binding APIs and feature selections. Two independent reviewers found no source/lock/documentation issues in the bounded delta. Existing reviews cover unchanged Rust/C# production code. No new advisory suppression.

Certificate dependency corrections: rustls-webpki0.103.16 and webpki-roots1.0.11 remove RUSTSEC-2026-0382/0381. Core floor follow-up remains bzsanti/oxidizePdf#831. Python lock is tracked; .NET lock remains ignored, so its exact graph is local evidence and CI resolves/audits independently.

Python: 3117 tests passed, 2 skipped; Clippy, parity and typing checks pass. Kripteia test/security analyses rerun for changed Python test scope; prior Rust/C# analyses remain applicable because those files are unchanged. Global Rust formatting has preexisting differences already recorded in the 5.5.3 review.

Audit still reports existing PyO30.28.3 advisories RUSTSEC-2026-0176/0177 and RSA RUSTSEC-2023-0071; baseline unsound/yanked warnings also remain. Core/certificate advisories0387/0381/0382 are absent. This is not a globally clean audit. Python PR remains draft pending separate PyO3 security follow-up.

Platform CI is pending at this local checkpoint. No new binding package has been published.
