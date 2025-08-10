# Scripts

Helper automation (frequency analysis, duplicate detection, SRS export, adaptive recommendation).

Before adding code:

- Add `requirements.txt` listing pinned versions if external libs used.
- Provide usage section in this README or per-script comments.

## Export Quizlet

```
python scripts\export_quizlet.py --input vocab --output quizlet_export.tsv
```

## Log Progress Attempt

```
python scripts\update_progress.py --skill reading --attempt-id read-2025-08-11-001 \\
	--source cam16-test2-p1 --comp-total 10 --comp-correct 7 \\
	--vocab-presented 10 --vocab-mastered 6 --time 780 --difficulty 3 --new-words pivotal emerge
```

Appends to `data/progress/progress.ndjson` and updates `current_level.json`.

## Recommend Vocab (Adaptive)

```
python scripts\recommend_vocab.py --vocab-dir vocab --count 15 --tsv recommended.tsv
```

Reads current level + exposure counts to produce a balanced set (core/stretch/challenge). Use `--json plan.json` for machine-readable output.

Flags:

- `--include-mastered` include high exposure words
- `--level-override B2` test a different target level
- `--mastery-threshold 3` change mastery definition

## Roadmap

- Add spaced interval scheduling (time-decay weighting)
- Integrate collocation difficulty scoring
- Provide Anki export format
