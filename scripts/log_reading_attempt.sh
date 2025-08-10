#!/usr/bin/env bash
# Quick helper to append a reading attempt & auto-use timestamp for attempt id.
# Usage: ./scripts/log_reading_attempt.sh source_id 10 7 10 6 780 295 "new words list"
# Args: source comp_total comp_correct vocab_presented vocab_mastered time_sec tokens "new words space-separated"
set -euo pipefail
if [ $# -lt 8 ]; then
  echo "Usage: $0 source comp_total comp_correct vocab_presented vocab_mastered time_sec tokens 'new words'" >&2
  exit 1
fi
src=$1; comp_total=$2; comp_correct=$3; vp=$4; vm=$5; t=$6; tokens=$7; shift 7; new_words=$*
stamp=$(date -u +%Y-%m-%dT%H%M%SZ)
attempt_id="read-${stamp}"
python3 scripts/update_progress.py --skill reading --attempt-id "$attempt_id" --source "$src" \
  --comp-total "$comp_total" --comp-correct "$comp_correct" --vocab-presented "$vp" \
  --vocab-mastered "$vm" --time "$t" --tokens "$tokens" --new-words $new_words
