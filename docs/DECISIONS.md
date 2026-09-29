# Decisions

- The workbook is authoritative. A missing `last_verified` cell remains NULL; user-facing output must identify that the source did not record a verification date.
- Where workbook document text explicitly connects a document and approval, mappings are indicative, marked for review, and never presented as authoritative requirements.
- The workbook contains no `last_verified` approval column and no document-to-approval mapping sheet. The import must preserve those data gaps instead of filling them with inferred facts.
- Existing working-tree edits predate this task. They are being preserved while requested fixes are applied on top.
