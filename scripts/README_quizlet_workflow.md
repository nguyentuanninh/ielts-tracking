# Quizlet Export & Progress Quick Workflow

## 1. After Generating Passage Files

You now have:

- `vocab/<slug>-vocab.tsv`
- `vocab/<slug>-collocations.tsv`
- `grammar/<slug>-grammar.md`

## 2. Merge for Quizlet Upload

```
python scripts/prepare-quizlet.py
```

Outputs (root):

- `quizlet_vocab_all.tsv`
- `quizlet_collocations_all.tsv`

Paste each into a new Quizlet set (Quizlet auto-detects TAB delimiter).

Options:

```
python scripts/prepare-quizlet.py --vocab-output export/my_vocab.tsv --colloc-output export/my_colloc.tsv
python scripts/prepare-quizlet.py --allow-duplicate-senses
```

## 3. Track Reading Attempt

Option A (shell helper):

```
bash scripts/log_reading_attempt.sh chronicle-of-timekeeping 10 7 65 50 780 295 "integral escapement"
```

Format:
source comp_total comp_correct vocab_presented vocab_mastered time_sec tokens "new words"

Option B (manual):

```
python scripts/update_progress.py --skill reading --attempt-id read-2025-08-11-001 \
  --source chronicle-of-timekeeping --comp-total 10 --comp-correct 7 \
  --vocab-presented 65 --vocab-mastered 50 --time 780 --tokens 295 \
  --new-words integral escapement
```

## 4. Check Level / Progress

```
cat data/progress/current_level.json
```

Append log file grows: `data/progress/progress.ndjson`.

## 5. Export Existing JSON Word Banks (if any)

```
python scripts/export_quizlet.py --input vocab --output legacy_quizlet.tsv
```

## 6. Tips

- Run merge script again after each new passage (it rewrites merged TSVs).
- Keep term definitions concise; avoid TAB characters inside fields.
- For spaced repetition later, keep raw TSVs; they can be reprocessed.
