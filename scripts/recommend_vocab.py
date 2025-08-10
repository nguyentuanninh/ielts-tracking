"""Recommend vocabulary items adapted to current learner CEFR level.

Heuristic overview:
- Determine current level from data/progress/current_level.json (default B1 if missing).
- Build exposure counts from progress.ndjson by counting occurrences of each word in new_words_added arrays.
- Mastery threshold: exposure_count >= 3 (treat as mastered -> lower priority unless for spaced review logic).
- Distributions (target percentages) for selection (approximate, will degrade gracefully if insufficient pool):
    B1:    core(B1/B1+) 70%, stretch(B2) 25%, challenge(C1) 5%
    B1+:   core(B2) 50%, review(low-exp B1) 40%, challenge(C1) 10%
    B2:    core(B2) 60%, stretch(C1) 30%, review(low-exp B1) 10%
    B2+:   core(C1) 70%, review(B2) 20%, consolidation(B1 low-exp) 10%
- CEFR labels not present in entries are inferred as 'UNK' and only used if pool is tiny.

Input vocab sources: one or more JSON files containing a list of entries with fields:
  word, cefr, meanings[], collocations[], examples[] (see project conventions)

Selection priority within a band:
  1. Low exposure (exposures < 2)
  2. Medium exposure (2) (for reinforcement quota of up to 20% inside that band)
  3. Random fallback

Outputs:
  - Prints summary table to stdout
  - Writes TSV (TERM<TAB>Definition) if --tsv specified
  - Writes JSON plan if --json specified

Usage examples:
  python scripts/recommend_vocab.py --vocab-dir vocab --count 15 --tsv recommended.tsv
  python scripts/recommend_vocab.py --vocab-dir vocab --json plan.json --include-mastered --count 30

Limitations:
  - Relies on new_words_added logs; accuracy improves as you log attempts consistently.
  - Does not space by time yet (future: decay weighting).
"""
from __future__ import annotations
import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

PROGRESS_DIR = Path("data/progress")
LEVEL_FILE = PROGRESS_DIR / "current_level.json"
LOG_FILE = PROGRESS_DIR / "progress.ndjson"

CEFR_ORDER = ["A1", "A2", "B1", "B1+", "B2", "B2+", "C1", "C2"]

DISTRIBUTIONS = {
    "B1": {"core": 0.70, "stretch": 0.25, "challenge": 0.05},
    "B1+": {"core": 0.40, "stretch": 0.50, "challenge": 0.10},  # core=review B1, stretch=B2
    "B2": {"core": 0.60, "stretch": 0.30, "challenge": 0.10},
    "B2+": {"core": 0.50, "stretch": 0.40, "challenge": 0.10},
}

# Mapping band meaning per level
BAND_MAP = {
    "B1": {"core": ["B1", "B1+"], "stretch": ["B2"], "challenge": ["C1"]},
    "B1+": {"core": ["B1"], "stretch": ["B2"], "challenge": ["C1"]},
    "B2": {"core": ["B2"], "stretch": ["C1"], "challenge": ["C2", "C1+"]},
    "B2+": {"core": ["B2", "B2+"], "stretch": ["C1"], "challenge": ["C2"]},
}


def load_level() -> str:
    if LEVEL_FILE.exists():
        try:
            data = json.loads(LEVEL_FILE.read_text(encoding="utf-8"))
            return data.get("current_cefr", "B1")
        except Exception:  # noqa: BLE001
            return "B1"
    return "B1"


def load_progress_exposures() -> Dict[str, int]:
    exposures: Dict[str, int] = {}
    if not LOG_FILE.exists():
        return exposures
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            words = obj.get("new_words_added") or []
            for w in words:
                if not isinstance(w, str):
                    continue
                exposures[w.lower()] = exposures.get(w.lower(), 0) + 1
    return exposures


def load_vocab_entries(vocab_dir: Path) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for jf in vocab_dir.glob("*.json"):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            if isinstance(data, list):
                entries.extend([e for e in data if isinstance(e, dict)])
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] skip {jf}: {e}", file=sys.stderr)
    return entries


def band_for_entry(level: str, cefr: str) -> str | None:
    level_map = BAND_MAP.get(level)
    if not level_map:
        # fallback treat as B1 mapping
        level_map = BAND_MAP["B1"]
    for band, cefrs in level_map.items():
        if cefr in cefrs:
            return band
    return None


def categorize(entries: List[Dict[str, Any]], level: str) -> Dict[str, List[Dict[str, Any]]]:
    buckets = {"core": [], "stretch": [], "challenge": []}
    for e in entries:
        cefr = e.get("cefr") or e.get("CEFR") or "UNK"
        b = band_for_entry(level, cefr)
        if b:
            buckets[b].append(e)
    return buckets


def select_from_bucket(bucket: List[Dict[str, Any]], need: int, exposures: Dict[str, int], include_mastered: bool, mastery_threshold: int) -> List[Dict[str, Any]]:
    if need <= 0 or not bucket:
        return []
    # Annotate with exposure
    annotated: List[Tuple[int, Dict[str, Any]]] = []
    for e in bucket:
        w = (e.get("word") or "").lower()
        exp = exposures.get(w, 0)
        if not include_mastered and exp >= mastery_threshold:
            continue
        annotated.append((exp, e))
    if not annotated:
        return []
    # Sort by exposure ascending (low first), then random shuffle within exposure tiers
    random.shuffle(annotated)
    annotated.sort(key=lambda x: x[0])
    return [e for _, e in annotated[:need]]


def build_definition(e: Dict[str, Any]) -> str:
    meanings = e.get("meanings") or []
    meaning = meanings[0] if meanings else ""
    pos = e.get("pos")
    cefr = e.get("cefr")
    colloc = e.get("collocations") or []
    parts = [meaning]
    meta = []
    if pos:
        meta.append(pos)
    if cefr:
        meta.append(cefr)
    if colloc:
        meta.append("Colloc: " + "; ".join(colloc[:2]))
    if meta:
        parts.append(" | ".join(meta))
    return " | ".join(p for p in parts if p)


def recommend(level: str, entries: List[Dict[str, Any]], count: int, exposures: Dict[str, int], include_mastered: bool, mastery_threshold: int) -> List[Dict[str, Any]]:
    dist = DISTRIBUTIONS.get(level) or DISTRIBUTIONS["B1"]
    buckets = categorize(entries, level)
    plan: List[Dict[str, Any]] = []
    # Calculate needs
    needs = {band: int(count * pct) for band, pct in dist.items()}
    # Adjust rounding remainder
    remainder = count - sum(needs.values())
    if remainder > 0:
        needs["core"] += remainder

    for band in ["core", "stretch", "challenge"]:
        selected = select_from_bucket(buckets[band], needs.get(band, 0), exposures, include_mastered, mastery_threshold)
        plan.extend(selected)

    # Fallback fill if short
    if len(plan) < count:
        pool = [e for e in entries if e not in plan]
        random.shuffle(pool)
        for e in pool:
            if len(plan) >= count:
                break
            w = (e.get("word") or "").lower()
            exp = exposures.get(w, 0)
            if not include_mastered and exp >= mastery_threshold:
                continue
            plan.append(e)
    return plan[:count]


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Recommend vocab list based on progress & level")
    ap.add_argument("--vocab-dir", default="vocab")
    ap.add_argument("--count", type=int, default=15)
    ap.add_argument("--include-mastered", action="store_true")
    ap.add_argument("--mastery-threshold", type=int, default=3)
    ap.add_argument("--tsv", help="Write TSV output path")
    ap.add_argument("--json", help="Write JSON plan path")
    ap.add_argument("--level-override", help="Override current level (e.g., B2)")
    return ap.parse_args(argv or sys.argv[1:])


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv)
    level = ns.level_override or load_level()
    exposures = load_progress_exposures()
    entries = load_vocab_entries(Path(ns.vocab_dir))
    if not entries:
        print("No vocab entries found", file=sys.stderr)
        return 1
    plan = recommend(level, entries, ns.count, exposures, ns.include_mastered, ns.mastery_threshold)

    # Output summary
    print(f"Level: {level} | Requested: {ns.count} | Provided: {len(plan)}")
    print("word\tcefr\texposures\tdefinition")
    for e in plan:
        w = e.get("word")
        cefr = e.get("cefr", "?")
        exp = exposures.get((w or '').lower(), 0)
        print(f"{w}\t{cefr}\t{exp}\t{build_definition(e)[:80]}")

    if ns.tsv:
        lines = [f"{e.get('word')}\t{build_definition(e)}" for e in plan]
        Path(ns.tsv).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[WROTE] TSV -> {ns.tsv}")
    if ns.json:
        out = []
        for e in plan:
            out.append({
                "word": e.get("word"),
                "cefr": e.get("cefr"),
                "exposures": exposures.get((e.get("word") or '').lower(), 0),
                "definition": build_definition(e),
            })
        Path(ns.json).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[WROTE] JSON -> {ns.json}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
