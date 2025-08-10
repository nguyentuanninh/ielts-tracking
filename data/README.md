# Data

Purpose: Store (a) source PDF scan references (metadata only) and (b) derived textual / statistical datasets produced from OCR. Avoid committing full copyrighted PDFs.

## What to Commit

- `metadata/` JSON or YAML describing each PDF (id, title, edition, page_range_used, permission_note, ocr_tool, ocr_date, checksum).
- `ocr/` cleaned text excerpts you are permitted to use (≤ allowed length; no full book units if restricted by copyright).
- `stats/` frequency lists, collocation counts, difficulty tagging outputs.

## What NOT to Commit

- Full scanned textbooks or full chapters (copyright risk).
- Raw large binary PDFs (>5MB) unless explicitly public-domain and necessary (else add to `.gitignore`).

## Suggested Subfolders

- `metadata/` – source descriptors.
- `ocr/` – plain text files named `<sourceId>-pXX-YY.txt`.
- `intermediate/` – temporary normalization outputs (can be gitignored if noisy).
- `stats/` – JSON/CSV frequency lists (`<sourceId>-freq.json`).

## OCR Workflow (Recommended)

1. Place raw PDFs outside repo (`/raw-pdf/` ignored).
2. Run OCR (e.g., Tesseract) -> produce UTF-8 text.
3. Normalize: strip headers/footers, fix common OCR errors (ﬁ -> fi), collapse multiple spaces.
4. Save permitted excerpt into `ocr/`.
5. Generate metadata entry capturing: source, pages used, purpose, license note.
6. Run frequency / collocation script -> output into `stats/` with method description.

## Metadata Minimal Schema (JSON example)

```
{
	"id": "cam16-test2-p1",
	"title": "Cambridge IELTS 16 Test 2 Passage 1 (excerpt)",
	"pages_used": "45-46",
	"excerpt_chars": 1834,
	"permission_note": "Study use; limited excerpt",
	"ocr_tool": "tesseract 5.3.0",
	"ocr_confidence_avg": 0.93,
	"created": "2025-08-11",
	"checksum_pdf_sha1": "<sha1>"
}
```

## METHOD.md

For any statistical dataset include a short `METHOD.md` describing:

- Input sources (ids)
- Processing steps (tokenization, stopword list, lemmatizer)
- Date & script version
- Known limitations (OCR noise %, excluded pages)

## Formatting

- Use LF line endings, UTF-8.
- Keep JSON compact (no trailing spaces). Pretty-print only for human-maintained files.

## Copyright Caution

Always verify that excerpt length complies with fair use / license. If unsure, do not commit.
