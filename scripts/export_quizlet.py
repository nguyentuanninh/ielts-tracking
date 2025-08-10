"""Export vocab JSON files into a Quizlet-friendly TSV.

Quizlet import format: each line = TERM<TAB>DEFINITION

Input assumptions:
- JSON file contains a list of vocab entry objects with at least: word, pos, meanings (list)
- Optional fields: cefr, collocations (list), examples (list), synonyms (list), antonyms (list), vn_meaning (string)

If vn_meaning present -> used as definition prefix; else first meaning.
Additional info (POS, CEFR, key collocations) appended to enrich definition.

Usage:
    python scripts/export_quizlet.py --input vocab --output quizlet_export.tsv

You can pass a directory (recursively scans *.json) or a single file.

Safety / Copyright: Only export items you authored or are allowed to share.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

EXCLUDED_FILENAMES = {"sample_list.template.json"}


def gather_json_files(path: Path) -> List[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() == ".json" else []
    return sorted(p for p in path.rglob("*.json") if p.name not in EXCLUDED_FILENAMES)


def load_entries(files: List[Path]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for obj in data:
                    if isinstance(obj, dict):
                        entries.append(obj)
            else:
                print(f"[WARN] {f} is not a list; skipped", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] Failed {f}: {e}", file=sys.stderr)
    return entries


def build_term_definition(entry: Dict[str, Any]) -> tuple[str, str]:
    word = entry.get("word") or entry.get("term")
    if not word:
        return ("", "")

    pos = entry.get("pos") or entry.get("part_of_speech")
    cefr = entry.get("cefr")
    vn_meaning = entry.get("vn_meaning")
    meanings: List[str] = [m for m in entry.get("meanings", []) if isinstance(m, str)]
    collocations: List[str] = [c for c in entry.get("collocations", []) if isinstance(c, str)]
    examples: List[str] = [e for e in entry.get("examples", []) if isinstance(e, str)]

    # Base definition preference: vn_meaning else first meaning (English)
    base_def = vn_meaning or (meanings[0] if meanings else "")

    # Compose supplementary info
    sup_parts: List[str] = []
    if pos:
        sup_parts.append(pos)
    if cefr:
        sup_parts.append(cefr)
    if collocations:
        sup_parts.append("Collocations: " + "; ".join(collocations[:3]))
    if examples:
        sup_parts.append("Ex: " + examples[0][:70])

    definition = base_def
    if sup_parts:
        definition += " | " + " | ".join(sup_parts)
    return (str(word), definition.strip())


def export(entries: List[Dict[str, Any]], out_file: Path, dedupe: bool = True) -> int:
    lines: List[str] = []
    seen = set()
    for e in entries:
        term, definition = build_term_definition(e)
        if not term or not definition:
            continue
        key = (term.lower(), definition.lower())
        if dedupe and key in seen:
            continue
        seen.add(key)
        # Sanitize tabs/newlines inside definition
        safe_def = definition.replace("\t", " ").replace("\n", " ")
        lines.append(f"{term}\t{safe_def}")

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def parse_args(argv: List[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Export vocab JSON to Quizlet TSV")
    ap.add_argument("--input", "-i", required=True, help="Input JSON file or directory containing JSON")
    ap.add_argument("--output", "-o", default="quizlet_export.tsv", help="Output TSV file path")
    ap.add_argument("--no-dedupe", action="store_true", help="Do not deduplicate term+definition pairs")
    return ap.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv or sys.argv[1:])
    in_path = Path(ns.input)
    if not in_path.exists():
        print(f"Input path not found: {in_path}", file=sys.stderr)
        return 1
    files = gather_json_files(in_path)
    if not files:
        print("No JSON vocab files found", file=sys.stderr)
        return 2
    entries = load_entries(files)
    count = export(entries, Path(ns.output), dedupe=not ns.no_dedupe)
    print(f"Exported {count} items -> {ns.output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
