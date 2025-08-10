# AI Coding Agent Instructions

Purpose: English learning & IELTS Reading note workspace (currently minimal). Keep instructions concise, actionable, updated as structure grows.

## Planned Structure

`vocab/` word lists | `texts/` passages | `exercises/` quizzes | `scripts/` helpers | `data/` derived stats

## Core Conventions

- Markdown for notes; JSON for structured banks (one logical concept per file if large).
- Filenames: scripts `kebab-case.py`; data `snake_case.json`; topical notes descriptive (e.g. `phrasal-verbs-travel.md`).
- Vocabulary entry minimal schema (YAML/Markdown block or JSON): word, pos, CEFR, meanings[], collocations[], examples[], synonyms[], antonyms[]. Keep examples ≤20 words, authentic.
- Wrap prose ~100 chars, no trailing whitespace. UTF-8 only.

### Sample Vocab Markdown Block

```
### word: ubiquitous
- pos: adjective | CEFR: C1 | IPA: /juːˈbɪkwɪtəs/
- Meaning: seeming to be everywhere
- Collocations: ubiquitous presence; ubiquitous computing
- Example: Smartphones are ubiquitous in modern society.
```

## IELTS Reading Analysis Agent Mode

User baseline: CEFR B1. Goal: surface learnable items pushing toward B2+/C1 without overload.
When given a passage (≤400 words per turn):

1. Read & extract 8–12 target lexical items (mix B2 core + 1–2 C1 stretch). Skip very basic B1 and ultra-rare words.
2. For each: form (word or collocation), concise VN meaning, one clear EN example (prefer original; else create), usage note (register, grammar pattern, nuance, common collocation frame).
3. Identify 2–5 grammar / sentence structures that illustrate upgrade value (e.g., reduced clause, inversion, complex noun phrase). Explain function + typical learner pitfall at B1.
4. List 5–8 academic / high‑utility collocations or discourse phrases enabling paraphrase (e.g., "a growing body of", "plays a pivotal role"). Brief use note.
5. Output sections exactly in order: Từ vựng | Ngữ pháp | Mẫu câu / Collocations. No full-text translation; no unrelated advice.
6. Language: Explanations may mix concise Vietnamese gloss + essential English (do not over-explain obvious B1 items).
7. If user requests practice: generate

- Vocabulary: gap-fill or matching using the extracted items.
- Grammar: transformation or identify-the-structure tasks.
- Collocations: collocation completion (provide stem + missing word).
  Provide answer key separately labeled.

Edge Handling:

- If passage >400 words: ask user to split; process first segment only.
- If insufficient advanced items: include fewer items, note limitation.

## Agent Workflow (General)

Small, atomic commits (topic-focused). Add scripts only with `requirements.txt` & usage snippet. Flag duplicates in vocab lists. Ask clarification only on ambiguity.

## Data Hygiene

No PII. Exclude oversized raw corpora; commit only processed summaries + generation script/method note.

## Evolve This File

Update once real directories appear (add test/CI rules, JSON schema validation, SRS export). Keep total length <70 lines.

Feedback Welcome: indicate unclear sections or additional workflows to codify (e.g., Anki export, frequency analysis pipeline).
