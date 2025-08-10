# Learner Progress Tracking

Goal: Track performance over time (Reading, Vocabulary, Writing) to adapt future item difficulty.

## Quick Start (Cách dùng nhanh)

1. Sau mỗi bài đọc / bài tập từ vựng: ghi log attempt

```
python scripts\update_progress.py --skill reading --attempt-id read-2025-08-11-001 \
  --source cam16-test2-p1 --comp-total 10 --comp-correct 7 \
  --vocab-presented 10 --vocab-mastered 6 --time 780 --tokens 295 \
  --new-words pivotal emerge inference
```

2. Kiểm tra level hiện tại trong: `data/progress/current_level.json` (fields: current_cefr, sublevel_code, proficiency_score, provisional).
3. Sinh danh sách từ phù hợp độ khó:

```
python scripts\recommend_vocab.py --vocab-dir vocab --count 15 --tsv recommended.tsv
```

4. (Tuỳ chọn) Xuất Quizlet:

```
python scripts\export_quizlet.py --input vocab --output quizlet_export.tsv
```

5. Lặp lại: Sau vài attempt xem score tăng (proficiency_score) và sublevel_code thay đổi.

### Ý nghĩa các file

- `progress.ndjson`: Lịch sử attempt (append-only). Mỗi dòng = 1 JSON.
- `current_level.json`: Trạng thái tổng hợp mới nhất (coarse CEFR + sublevel + score).

### Giải thích các chỉ số chính

- comprehension% = comp_questions_correct / comp_questions_total \* 100
- retention% = vocab_items_mastered / vocab_items_presented \* 100
- attempt_score (0–100) = kết hợp comprehension, retention, speed (nếu có) trừ lỗi.
- proficiency_score = trung bình có trọng số giảm dần 7 attempt đọc gần nhất.
- sublevel_code = mã chi tiết (B1.3, B1.8, B2.1 …) để điều chỉnh độ khó.

### Khi nào nâng sublevel nhanh?

- Giữ comprehension >=70% + retention >=50% nhiều lần liên tiếp.
- Thêm tokens/time để tính speed_norm (tăng base score nếu đọc đủ nhanh >90 wpm).
- Giảm lỗi inference (nặng nhất trong penalty).

### Điều chỉnh / Tinh chỉnh

- Muốn thay ngưỡng mastery: sửa logic trong `update_progress.py` (map_sublevel hoặc trọng số).
- Muốn thêm kỹ năng riêng (writing): thêm tính toán attempt_score chuyên biệt khác (mở rộng script).
- Muốn spaced repetition: sẽ cần decay exposure trong recommend_vocab.py (chưa làm).

### Troubleshooting

- Score không tăng: kiểm tra comp_questions_total >0 và vocab_items_presented >0; đảm bảo nhập đúng tokens/time.
- sublevel không đổi nhưng proficiency_score thay đổi ít (<0.01): ngưỡng mapping chưa vượt; cần thêm vài attempt nữa.
- Lỗi JSON dòng hỏng: xoá dòng lỗi khỏi `progress.ndjson` (backup trước) rồi chạy lại.

### Best Practices

- Đặt attempt_id có pattern: `read-YYYY-MM-DD-###` để dễ sort.
- Ghi từ mới vào `--new-words` đúng chính tả để exposure đếm chính xác.
- Không chỉnh tay `current_level.json` trừ khi reset.

---

## Core Concepts

- attempt: A single completed task (reading analysis, vocab exercise, writing sample review).
- skill_focus: Primary skill targeted (reading, vocab, grammar, writing, mixed).
- baseline_cefr_estimate: Rolling estimate before this attempt.
- outcome metrics: comprehension_rate, accuracy, time_spent_sec, new_words_retained.

## File Format

Use newline-delimited JSON (NDJSON) for append-only log: one JSON object per line (`progress.ndjson`). Easier to append & parse incrementally.

## Minimal Schema (fields optional unless marked \*)

```
{
  "timestamp": "2025-08-11T09:35:12Z", *
  "attempt_id": "read-2025-08-11-001", *
  "skill_focus": "reading", *
  "source_id": "cam16-test2-p1",
  "input_tokens": 295,
  "baseline_cefr_estimate": "B1",
  "target_cefr": "B2",
  "self_rating_difficulty": 3,        // 1(easy)-5(very hard)
  "time_spent_sec": 780,
  "comp_questions_total": 10,
  "comp_questions_correct": 7,
  "vocab_items_presented": 10,
  "vocab_items_mastered": 6,
  "new_words_added": ["pivotal", "emerge"],
  "errors_types": {"inference": 2, "detail": 1},
  "notes": "Struggled with inference; pacing okay." ,
  "system_cefr_update": "B1+"        // model-adjusted after processing
}
```

## Rolling CEFR Estimation (Heuristic)

- Start: declared baseline (B1).
- Promote to B1+ when: last 3 reading attempts show >=70% comprehension and >=50% vocab retention.
- Promote to B2 when: last 5 attempts avg comprehension >=75% and vocab retention >=60%; inference errors <=20% of total errors.
- Demote (temporary) if two consecutive attempts <50% comprehension.
  Store current estimate separately in `current_level.json`.

### `current_level.json` Example

```
{ "current_cefr": "B1", "last_update": "2025-08-11T09:35:12Z" }
```

## Workflow

1. After each exercise/reading, append an attempt object to `progress.ndjson`.
2. Recompute rolling metrics & update `current_level.json`.
3. Future generation scripts read these to adjust difficulty (e.g., choose C1 stretch items only if current_cefr >= B2-).

## Granular Proficiency Score (New)

Besides coarse CEFR bands, we maintain a continuous `proficiency_score` (0–100) and a derived sublevel (e.g. `B1.3`, `B1.8`, `B2.1`). This reduces big jumps.

### Attempt Score Formula (Reading)

For each reading attempt we compute an `attempt_score` (0–100):

```
comp = comprehension%                # (correct / total * 100)
vocab = retention%                   # (mastered / presented * 100)
speed_norm = clip( (wpm - 90) / (180 - 90), 0, 1 ) * 100   # if input_tokens present
error_penalty =  (inference_errors * 4 + other_errors * 2)
               / max(comp_questions_total,1) * 15          # scaled 0–15
base = 0.5*comp + 0.3*vocab + 0.2*speed_norm
attempt_score = max(0, base - error_penalty)
```

If speed data missing, weight is redistributed proportionally to comp & vocab (0.625*comp + 0.375*vocab).

### Rolling Proficiency

`proficiency_score` = weighted mean of last up to 7 reading attempt_scores with exponential decay (weights: 1, 0.85, 0.72, ...). Minimum 3 attempts before trusting (> status `provisional`: true until then).

### Mapping Score -> Sublevel & CEFR (example)

```
0–34  -> B1.0 (B1-)
35–49 -> B1.3 (B1)
50–59 -> B1.8 (B1+)
60–69 -> B2.1 (B2-)
70–79 -> B2.4 (B2)
80–86 -> B2.7 (B2+)
87–93 -> C1.1 (C1-)
94–100-> C1.4 (C1)
```

We store `current_cefr` (coarse) + `sublevel_code` + `proficiency_score`.

### current_level.json Extended Example

```
{
  "current_cefr": "B1",
  "sublevel_code": "B1.3",
  "proficiency_score": 47.2,
  "provisional": true,
  "last_update": "2025-08-11T09:50:40Z"
}
```

### Why This Helps

- Fine-grained adaptation for vocab selection (e.g., choose 2 C1 stretch items only if score >= 70).
- Detect micro-progress earlier (motivation).
- Smooths volatility via decay weighting.

### Future Extensions

- Time-decay on vocab retention (forgetting curve)
- Separate subscores per skill (reading_speed_score, inference_score)
- Confidence intervals when attempts < threshold

## Privacy

Do not store personal identifiers. Only performance metrics.

## Next Automation

A script `update_progress.py` can:

- Append new attempt.
- Recalculate CEFR level using heuristic.
- Provide summary stats (last N attempts).
- Compute attempt_score + rolling proficiency_score + sublevel_code.
