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

### Tự Động Tạo Set Quizlet (Playwright)

(Beta – có thể hỏng khi Quizlet đổi giao diện; dùng cá nhân.)

1. Cài phụ thuộc:
   ```
   pip install -r scripts/requirements.txt
   playwright install
   ```
2. Xuất 2 file TSV (vocab & collocations) như bình thường.
3. Đặt biến môi trường đăng nhập (không commit):
   ```
   export QUIZLET_USER="email_or_username"
   export QUIZLET_PASS="your_password"
   # Hoặc dùng file .env (không commit) + direnv
   ```
4. Chạy script (ví dụ headful + chọn folder có sẵn "IELTS Daily"):
   ```
   python3 scripts/quizlet_playwright.py \
     --vocab-file vocab/chronicle-of-timekeeping-vocab.tsv \
     --collocation-file vocab/chronicle-of-timekeeping-collocations.tsv \
     --folder "IELTS with Ms.Tam" --headful
   ```
5. Script tạo 2 set với tiêu đề dạng `DD/MM vocab` và `DD/MM collocation` (vd 11/08 vocab). Dùng `--date 10/08` để override.

Flags hữu ích:

- `--slowmo 150` nhìn thao tác rõ.
- `--debug` in console.
- `--auto-close` đóng browser sau khi tạo (mặc định giữ mở khi headful).

Lưu ý bảo mật: không hardcode password; nếu đã lộ đổi mật khẩu ngay.

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
