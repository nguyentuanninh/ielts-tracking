"""Append a learner attempt to progress log and update rolling CEFR & granular proficiency.

CEFR Heuristic (must sync with data/progress/README.md):
- Promote to B1+ when last 3 reading attempts comprehension >=70% AND vocab retention >=50%.
- Promote to B2 when last 5 reading attempts avg comprehension >=75% AND vocab retention >=60% AND inference errors <=20%.
- Demote if two consecutive reading attempts comprehension <50%.

Granular proficiency:
- Compute attempt_score (0–100) combining comprehension, vocab retention, speed (if tokens/time available) and error penalty.
- Rolling proficiency_score = exp-decay weighted mean of last up to 7 reading attempt_scores.
- Map to sublevel_code (e.g., B1.3, B2.1) + coarse CEFR.

Usage:
    python scripts/update_progress.py --skill reading --attempt-id read-2025-08-11-002 \
        --source cam16-test2-p1 --comp-total 10 --comp-correct 8 \
        --vocab-presented 10 --vocab-mastered 7 --time 650 --difficulty 3 \
        --new-words pivotal emerge --tokens 300

Extend as needed; pure stdlib.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROGRESS_DIR = Path("data/progress")
LOG_FILE = PROGRESS_DIR / "progress.ndjson"
LEVEL_FILE = PROGRESS_DIR / "current_level.json"


def load_attempts(limit: int | None = None) -> List[Dict[str, Any]]:
    if not LOG_FILE.exists():
        return []
    attempts: List[Dict[str, Any]] = []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                attempts.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"[WARN] Skipping malformed line: {line[:50]}", file=sys.stderr)
    return attempts[-limit:] if limit else attempts


def load_level() -> Dict[str, Any]:
    if LEVEL_FILE.exists():
        try:
            return json.loads(LEVEL_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {"current_cefr": "B1", "last_update": None}


def save_level(level: Dict[str, Any]) -> None:
    LEVEL_FILE.write_text(json.dumps(level, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compute_comprehension(a: Dict[str, Any]) -> float:
    tot = a.get("comp_questions_total") or 0
    cor = a.get("comp_questions_correct") or 0
    return (cor / tot) * 100 if tot else 0.0


def compute_vocab_retention(a: Dict[str, Any]) -> float:
    pres = a.get("vocab_items_presented") or 0
    mast = a.get("vocab_items_mastered") or 0
    return (mast / pres) * 100 if pres else 0.0


def infer_level(attempts: List[Dict[str, Any]], current: str) -> str:
    reading_attempts = [a for a in attempts if a.get("skill_focus") == "reading"]
    last3 = reading_attempts[-3:]
    last5 = reading_attempts[-5:]

    def avg(metric_fn, arr):
        return sum(metric_fn(a) for a in arr) / len(arr) if arr else 0.0

    # Demotion check
    if len(reading_attempts) >= 2 and all(compute_comprehension(a) < 50 for a in reading_attempts[-2:]):
        if current not in {"B1", "B1-"}:
            return "B1"  # reset to safer baseline

    # Promotion rules
    if current in {"B1", "B1-"} and len(last3) == 3:
        if all(compute_comprehension(a) >= 70 for a in last3) and all(compute_vocab_retention(a) >= 50 for a in last3):
            return "B1+"
    if current in {"B1+", "B1"} and len(last5) == 5:
        comp_avg = avg(compute_comprehension, last5)
        vocab_avg = avg(compute_vocab_retention, last5)
        # inference errors proportion
        total_inf = sum((a.get("errors_types", {}) or {}).get("inference", 0) for a in last5)
        total_err = sum(sum((a.get("errors_types", {}) or {}).values()) for a in last5) or 1
        inference_ratio = total_inf / total_err
        if comp_avg >= 75 and vocab_avg >= 60 and inference_ratio <= 0.2:
            return "B2"
    return current


def append_attempt(data: Dict[str, Any]) -> None:
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Append learner attempt & update CEFR")
    ap.add_argument("--skill", required=True, choices=["reading", "vocab", "grammar", "writing", "mixed"], dest="skill")
    ap.add_argument("--attempt-id", required=True)
    ap.add_argument("--source", dest="source_id")
    ap.add_argument("--comp-total", type=int, dest="comp_total")
    ap.add_argument("--comp-correct", type=int, dest="comp_correct")
    ap.add_argument("--vocab-presented", type=int, dest="vocab_presented")
    ap.add_argument("--vocab-mastered", type=int, dest="vocab_mastered")
    ap.add_argument("--time", type=int, dest="time_spent_sec")
    ap.add_argument("--difficulty", type=int, dest="self_rating_difficulty")
    ap.add_argument("--new-words", nargs="*", dest="new_words")
    ap.add_argument("--baseline", dest="baseline_cefr")
    ap.add_argument("--tokens", type=int, dest="input_tokens", help="Token (word) count for reading speed calc")
    return ap.parse_args(argv or sys.argv[1:])


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv)
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    attempts = load_attempts()
    level = load_level()
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    attempt = {
        "timestamp": now_iso,
        "attempt_id": ns.attempt_id,
        "skill_focus": ns.skill,
        "source_id": ns.source_id,
        "baseline_cefr_estimate": ns.baseline_cefr or level.get("current_cefr"),
        "time_spent_sec": ns.time_spent_sec,
        "input_tokens": ns.input_tokens,
        "comp_questions_total": ns.comp_total,
        "comp_questions_correct": ns.comp_correct,
        "vocab_items_presented": ns.vocab_presented,
        "vocab_items_mastered": ns.vocab_mastered,
        "new_words_added": ns.new_words,
    }
    append_attempt(attempt)
    attempts.append(attempt)

    # Calculate granular proficiency for reading attempts
    reading_attempts = [a for a in attempts if a.get("skill_focus") == "reading"]

    def attempt_score(a: Dict[str, Any]) -> float:
        comp = compute_comprehension(a)
        vocab = compute_vocab_retention(a)
        tokens = a.get("input_tokens") or 0
        time_sec = a.get("time_spent_sec") or 0
        # Words per minute (approx tokens as words)
        if tokens > 0 and time_sec and time_sec > 0:
            wpm = (tokens / time_sec) * 60
            speed_norm = max(0.0, min(1.0, (wpm - 90) / (180 - 90))) * 100  # clamp
            comp_w, vocab_w, speed_w = 0.5, 0.3, 0.2
            base = comp_w * comp + vocab_w * vocab + speed_w * speed_norm
        else:
            # redistribute speed weight
            comp_w, vocab_w = 0.625, 0.375
            base = comp_w * comp + vocab_w * vocab
        # error penalty (if errors_types present)
        errors = a.get("errors_types") or {}
        inf_err = errors.get("inference", 0)
        other_err = sum(v for k, v in errors.items() if k != "inference")
        total_q = a.get("comp_questions_total") or 1
        error_pen = ((inf_err * 4) + (other_err * 2)) / total_q * 15
        return max(0.0, base - error_pen)

    def rolling_proficiency(r_attempts: List[Dict[str, Any]]) -> Tuple[float, bool]:
        if not r_attempts:
            return 0.0, True
        # last up to 7
        last = r_attempts[-7:]
        weights = []
        w = 1.0
        for _ in range(len(last)):
            weights.append(w)
            w *= 0.85  # decay
        weights = list(reversed(weights))  # align earliest with lowest index
        scores = [attempt_score(a) for a in last]
        total_w = sum(weights) or 1
        prof = sum(s * wt for s, wt in zip(scores, weights)) / total_w
        provisional = len(r_attempts) < 3
        return prof, provisional

    def map_sublevel(score: float) -> Tuple[str, str]:
        # returns (sublevel_code, coarse_cefr)
        if score < 35:
            return "B1.0", "B1"
        if score < 50:
            return "B1.3", "B1"
        if score < 60:
            return "B1.8", "B1+"
        if score < 70:
            return "B2.1", "B2"
        if score < 80:
            return "B2.4", "B2"
        if score < 87:
            return "B2.7", "B2+"
        if score < 94:
            return "C1.1", "C1"
        return "C1.4", "C1"

    prof_score, provisional = rolling_proficiency(reading_attempts)

    new_level = infer_level(attempts, level.get("current_cefr", "B1"))
    sub_code, coarse_from_score = map_sublevel(prof_score)
    # If heuristic coarse CEFR and score-based coarse disagree, keep higher only if not provisional
    if not provisional:
        # coarse_from_score may refine within band; choose higher by simple ranking
        rank = ["A1","A2","B1","B1+","B2","B2+","C1","C2"]
        if rank.index(coarse_from_score.replace("+","")) > rank.index(new_level.replace("+","")):
            new_level = coarse_from_score

    if (new_level != level.get("current_cefr")) or ("proficiency_score" not in level) or abs(level.get("proficiency_score",0)-prof_score) > 0.01:
        level = {
            "current_cefr": new_level,
            "sublevel_code": sub_code,
            "proficiency_score": round(prof_score, 2),
            "provisional": provisional,
            "last_update": now_iso,
        }
        save_level(level)
        print(f"Level updated -> {new_level} ({sub_code}) score={prof_score:.1f} provisional={provisional}")
    else:
        save_level(level)
        print(f"Level unchanged ({level.get('current_cefr')}) ({level.get('sublevel_code')}) score={prof_score:.1f}")

    # Quick summary
    last5 = [a for a in reading_attempts][-5:]
    if last5:
        comp_avg = sum(compute_comprehension(a) for a in last5) / len(last5)
        vocab_attempts = [a for a in last5 if (a.get("vocab_items_presented") or 0) > 0]
        vocab_avg = sum(compute_vocab_retention(a) for a in vocab_attempts) / (len(vocab_attempts) or 1)
        print(f"Last {len(last5)} reading attempts: comp_avg={comp_avg:.1f}% vocab_avg={vocab_avg:.1f}% prof={prof_score:.1f}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
