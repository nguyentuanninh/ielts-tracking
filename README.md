# English Learning Workspace

Tổng hợp hướng dẫn sử dụng hệ thống tracking tiến độ + xuất Quizlet + đề xuất từ vựng thích ứng.

## Cấu trúc Thư Mục Chính

```
vocab/        # Danh sách từ vựng (JSON hoặc Markdown)
texts/        # Đoạn đọc / nguồn (excerpt hợp lệ)
exercises/    # Bài tập tạo ra từ texts + vocab
scripts/      # Script tự động hóa
data/         # Dữ liệu dẫn xuất (progress, ocr, stats)
  progress/   # progress.ndjson + current_level.json
```

## Yêu Cầu

- Python 3.10+ (Windows hoặc Ubuntu). Không cần thư viện ngoài (stdlib).

## Quick Start

1. (Tuỳ chọn) Thêm từ vựng vào `vocab/*.json` theo schema mẫu.
2. Sau mỗi bài đọc / luyện: ghi 1 attempt.
3. Xem level chi tiết (CEFR + sublevel + proficiency_score).
4. Sinh danh sách từ vựng phù hợp độ khó.
5. Xuất TSV import vào Quizlet.

## Ghi Attempt (Progress Tracking)

Windows (cmd):

```
python scripts\update_progress.py --skill reading --attempt-id read-2025-08-11-001 ^
  --source cam16-test2-p1 --comp-total 10 --comp-correct 7 ^
  --vocab-presented 10 --vocab-mastered 6 --time 780 --tokens 295 ^
  --new-words pivotal emerge inference
```

Ubuntu / WSL:

```
python3 scripts/update_progress.py --skill reading --attempt-id read-2025-08-11-001 \
  --source cam16-test2-p1 --comp-total 10 --comp-correct 7 \
  --vocab-presented 10 --vocab-mastered 6 --time 780 --tokens 295 \
  --new-words pivotal emerge inference
```

Kết quả:

- Append dòng JSON vào `data/progress/progress.ndjson`
- Cập nhật `data/progress/current_level.json` với: current_cefr, sublevel_code, proficiency_score, provisional.

Chi tiết công thức & mapping: xem `data/progress/README.md`.

## Đề Xuất Từ Vựng Thích Ứng

Dựa trên level + tần suất xuất hiện (exposures) của từ mới trong log.

Windows:

```
python scripts\recommend_vocab.py --vocab-dir vocab --count 15 --tsv recommended.tsv
```

Ubuntu:

```
python3 scripts/recommend_vocab.py --vocab-dir vocab --count 15 --tsv recommended.tsv
```

Output: bảng ra stdout + file TSV (TERM<TAB>DEFINITION). Có thể thêm `--json plan.json`.

Các flag hữu ích:

- `--include-mastered` vẫn chọn từ đã gặp nhiều lần.
- `--level-override B2` thử giả lập level khác.
- `--mastery-threshold 3` đổi ngưỡng xem là đã quen.

## Xuất Quizlet

Windows:

```
python scripts\export_quizlet.py --input vocab --output quizlet_export.tsv
```

Ubuntu:

```
python3 scripts/export_quizlet.py --input vocab --output quizlet_export.tsv
```

Truy cập Quizlet -> Create -> Import -> dán nội dung TSV.

## Quy Ước Từ Vựng (JSON)

```
[
  {
    "word": "sustainable",
    "pos": "adjective",
    "cefr": "B2",
    "meanings": ["able to continue over time without causing damage"],
    "collocations": ["sustainable development", "sustainable practices"],
    "examples": ["We must invest in sustainable energy."],
    "synonyms": ["viable"],
    "antonyms": ["unsustainable"]
  }
]
```

## Quy Trình Chuẩn Hàng Ngày

1. Chọn đoạn đọc hợp lệ (≤400 từ) và xử lý học.
2. Log attempt với kết quả comprehension & vocab.
3. Xem `proficiency_score` tăng/giảm -> điều chỉnh mục tiêu.
4. Sinh danh sách từ mới + tạo bài tập.
5. Xuất Quizlet nếu cần ôn flashcard.

## Troubleshooting

- Score không tăng: kiểm tra đã nhập `--comp-total` >0 & `--vocab-presented` >0.
- Không có speed_norm: thêm `--tokens` + `--time` (giây).
- TSV lỗi tab: mở file bằng editor UTF-8 (không dùng Excel tự chuyển delimiter sai).

## Nâng Cấp Sắp Tới (Gợi ý)

- Spaced repetition decay exposures
- Weekly summary report script
- Subscores riêng (inference vs detail)
- Anki export

## Giấy Phép / Bản Quyền

Chỉ lưu excerpt được phép; không commit sách PDF nguyên gốc.

---

Feedback: chỉnh phần nào? Thêm tiếng Việt sâu hơn hay giữ gọn?
