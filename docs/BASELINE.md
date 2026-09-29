# Baseline acceptance status

The requested workbook oracle and golden HTTP tests did not exist when this task began. Initial code inspection found these known failures before the requested work:

- The importer substitutes today's date when the workbook has no verification date.
- Approval rules with unknown approval IDs are skipped rather than rejected.
- Invalid rule JSON is silently converted to a summary string.
- The importer adds a 24th supplemental document and hard-coded approval-document mappings that are not explicitly grounded in workbook text.
- The rules evaluator discards `Not applicable` matches and cannot expose category-specific outcomes.
- The approval API response requires a non-null verification date.

The new `test_excel_golden.py` imports the workbook to temporary SQLite, compares rule results against the independent reader, and checks the workbook's counts and grounded Q&A cases. The first broad run against inherited older tests exposed demo-era date/name assumptions and an empty RAG corpus. Those tests were updated to match workbook-backed records. Final verification: **79 passed, 1 skipped**; frontend production build succeeds.
