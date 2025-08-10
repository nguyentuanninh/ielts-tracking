# AI Coding Agent Instructions

Purpose: English learning & IELTS Reading note workspace. Keep concise, actionable, updated as structure grows.

## Planned Structure

`vocab/` word lists | `texts/` passages | `exercises/` quizzes | `scripts/` helpers | `data/` derived stats | `grammar/` analyses

## Core Conventions

- Markdown for notes; JSON for structured banks (one logical concept per file if large).
- Filenames: scripts `kebab-case.py`; data `snake_case.json`; topical notes descriptive (e.g. `phrasal-verbs-travel.md`).
- Vocabulary entry minimal schema (YAML/Markdown or JSON): word, pos, CEFR, meanings[], collocations[], examples (≤20 words, authentic), synonyms[], antonyms[].
- Wrap prose ~100 chars, no trailing spaces. UTF-8 only.

### Sample Vocab Markdown Block

```
### word: ubiquitous
- pos: adjective | CEFR: C1 | IPA: /juːˈbɪkwɪtəs/
- Meaning: seeming to be everywhere
- Collocations: ubiquitous presence; ubiquitous computing
- Example: Smartphones are ubiquitous in modern society.
```

## IELTS Reading Analysis Agent Mode

User baseline B1; surface all learnable items (B1 core reinforce, B2 core, C1 stretch).
When given a passage (any length, including screenshot OCR if needed):

1. If >1500 words, silently chunk (~300–400 words), process sequentially, merge outputs, report total chunks.
2. Lexical extraction (MAX coverage mode by default): include ALL content words & multi‑word items except only the most elementary A1 core (be, have, do, go, come, get, very, good, big, small, basic pronouns, days/months unless part of term). Include: phrasal verbs, multi‑word nouns, proper nouns with domain value, nominalised forms, word families (root + derived in text), hyphen compounds, number-based expressions, Latin/Greek origin academic terms. For each unique lemma: form | CEFR (est.) | concise VN meaning | EN example (trimmed original else crafted) | usage note (collocation/register/grammar) | optional freq band (H/M/L). Merge duplicates (append new collocation examples only). Borderline A2 but context‑specific or likely unknown to B1 user = INCLUDE (tag A2*). Mark skipped candidates (rare) only if user asks "why" (then label skipped-basic). Warn & split Parts if >160 items (hard cap 200; still file all). User can request density modes: "standard" (exclude A2* + high‑freq B1 obvious) or "max" (default) or "focus <theme>" (filter thematic subset after full internal list).
3. Grammar/structures: list ALL notable forms (reduced clauses, participial phrases, inversion, cleft, complex noun phrases, relative types, modality nuance, hedging, referencing devices). For each: short excerpt, function, common B1 pitfall, upgrade tip.
4. Discourse & paraphrase bank: academic/high‑utility collocations & cohesive phrases (no random single verbs) with brief use note (pattern/semantic role). Unlimited.
5. Output (inline response) sections strictly: Từ vựng | Ngữ pháp | Mẫu câu / Collocations. No full-text translation; no unrelated advice.
6. Practice on explicit request only ("Practice"): create Vocabulary (gap-fill/matching; if >60 sampled 25 note sampling) + Grammar (identify/transform) + Collocations (completion). Provide answer key.
7. File generation (auto on each new passage screenshot/text unless user opts out):
   - Generate slug from title or first 4–5 keywords lowercase hyphen (e.g. `chronicle-of-timekeeping`).
   - Create `vocab/<slug>-vocab.tsv`: tab-separated for Quizlet (Term<TAB>Definition). Term = word or expression; Definition = VN gloss + short EN usage + (CEFR). One line per unique item (B1/B2/C1 + A2\* included). Avoid tabs inside fields; semicolons for multiple senses.
   - Create `vocab/<slug>-collocations.tsv`: collocation/expression<TAB>VN meaning / function + EN pattern note.
   - Create `grammar/<slug>-grammar.md`: detailed grammar/structure list (expanded explanations, numbered, can reuse extraction but elaborated examples + mini practice placeholders). Heading: `# Grammar – <Slug>` then (Structures, Explanations, Common Pitfalls, Upgrade Tips, Mini Practice).
8. Ensure idempotent update: if files exist, append only NEW items (avoid duplicates) and note "(updated)" in commit message.
9. On OCR need (image only), ask for text if extraction ambiguous; otherwise proceed.
10. Overload handling: if >200 vocab lines, state suggestion to prioritize thematic subset first (still output full list/files). Provide optional frequency-sorted auxiliary list if >120.

## Agent Workflow (General)

Small, atomic commits. Scripts require `requirements.txt` & usage snippet. Flag duplicates in vocab lists. Ask clarification only if blocking.

## Data Hygiene

No PII. Exclude oversized raw corpora; commit only processed summaries + generation script/method note.

## Evolve This File

Update as directories/features grow (add CI/test rules, JSON schema validation, SRS export). Keep <70 lines total.

Feedback welcome: request clarifications or new workflows (Anki export, frequency analysis pipeline).
