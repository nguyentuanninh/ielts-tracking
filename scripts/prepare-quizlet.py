#!/usr/bin/env python3
"""Merge generated *-vocab.tsv and *-collocations.tsv into Quizlet‑ready TSVs.

Each source TSV: TERM<TAB>DEFINITION (no header).
Output files default: quizlet_vocab_all.tsv / quizlet_collocations_all.tsv (in project root) unless overridden.

Deduplication: keep first occurrence of a term (case‑insensitive). Optionally append new unique senses with suffix (use --allow-duplicate-senses).

Usage examples:
  python scripts/prepare-quizlet.py
  python scripts/prepare-quizlet.py --vocab-output export/my_vocab.tsv --colloc-output export/my_colloc.tsv

After running: open Quizlet > Create set > Paste entire TSV (it auto splits by TAB).
"""
from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Tuple

VOCAB_GLOB = "*-vocab.tsv"
COLLOC_GLOB = "*-collocations.tsv"


def read_tsv_lines(files: List[Path]) -> List[Tuple[str, str, Path]]:
    rows: List[Tuple[str, str, Path]] = []
    for f in files:
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                if "\t" not in line:
                    continue  # skip malformed
                term, definition = line.split("\t", 1)
                rows.append((term.strip(), definition.strip(), f))
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] Failed reading {f}: {e}")
    return rows


def merge(rows: List[Tuple[str, str, Path]], allow_dup_senses: bool) -> List[str]:
    out: List[str] = []
    seen_terms: set[str] = set()
    term_counts: dict[str, int] = {}
    for term, definition, _src in rows:
        key = term.lower()
        if key not in seen_terms:
            seen_terms.add(key)
            term_counts[key] = 1
            out.append(f"{term}\t{definition}")
        else:
            if allow_dup_senses:
                term_counts[key] += 1
                out.append(f"{term} ({term_counts[key]})\t{definition}")
            # else skip duplicate term
    return out


def write_output(lines: List[str], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def gather(pattern: str, base: Path) -> List[Path]:
    return sorted(base.glob(pattern))


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Merge vocab & collocation TSVs for Quizlet upload")
    ap.add_argument("--base-dir", default="vocab", help="Directory containing generated TSVs")
    ap.add_argument("--vocab-output", default="quizlet_vocab_all.tsv")
    ap.add_argument("--colloc-output", default="quizlet_collocations_all.tsv")
    ap.add_argument("--allow-duplicate-senses", action="store_true", help="Keep duplicate term with numbered suffix")
    return ap.parse_args()


def main() -> int:
    ns = parse_args()
    base = Path(ns.base_dir)
    vocab_files = gather(VOCAB_GLOB, base)
    colloc_files = gather(COLLOC_GLOB, base)
    if not vocab_files and not colloc_files:
        print(f"No TSV files found under {base}")
        return 1
    if vocab_files:
        vocab_rows = read_tsv_lines(vocab_files)
        vocab_out = merge(vocab_rows, ns.allow_duplicate_senses)
        c = write_output(vocab_out, Path(ns.vocab_output))
        print(f"Wrote {c} vocab terms -> {ns.vocab_output}")
    if colloc_files:
        colloc_rows = read_tsv_lines(colloc_files)
        colloc_out = merge(colloc_rows, ns.allow_duplicate_senses)
        c2 = write_output(colloc_out, Path(ns.colloc_output))
        print(f"Wrote {c2} collocations -> {ns.colloc_output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
