# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit <N>`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| `tone_ok` (`data/eval/judge_tone_public.csv`) | 100 | 0.757 | 0.857 | 0.8 | Có (κ=0.757≥0.6, P=0.857≥0.8, R=0.800≥0.7) | **dùng** |
| `helpful` (`data/eval/judge_helpful_public.csv`) | 100 | 0.375 | 1.0 | 0.3 | Không (κ=0.375<0.6, R=0.300<0.7) | **loại** |

## Audit thủ công (10 bất đồng từ `judge_tone_public.csv` + các nhóm bất đồng chính của `judge_helpful_public.csv`)

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & hành động sửa rubric / nhãn |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`) | `PASS` | `FAIL` | Người đúng | `"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."` — Xưng `"em"` + `"nha"` quá suồng sã; judge hiểu nhầm là thân thiện. **Sửa rubric:** quy định rõ xưng hô chuẩn CSKH (`LogiX` / `anh/chị`), cấm từ ngữ suồng sã (`nha`, `em-anh`). |
| 2 | `H-017` (`tone_ok`) | `PASS` | `FAIL` | Người đúng | `"Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha."` — Dùng `"bạn ơi"`, `"rồi nha"` thiếu trang trọng. **Sửa rubric:** bổ sung negative examples cho xưng hô `"bạn"` và đuôi câu `"nha/nhé"`. |
| 3 | `H-029` (`tone_ok`) | `PASS` | `FAIL` | Người đúng | `"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."` — Có `"Dạ, vui lòng"` ở đầu nhưng vế sau ra lệnh đuổi khách (`"không cần nhắn thêm"`). **Sửa rubric:** đánh `FAIL` ngay nếu có cụm ra lệnh/ngăn khách phản hồi bất kể từ mở đầu lịch sự. |
| 4 | `H-042` (`tone_ok`) | `FAIL` | `PASS` | Người đúng | `"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."` — Ngắn gọn, đầy đủ thông tin và lịch sự; judge phạt oan vì tưởng "thiếu xin lỗi". **Sửa rubric:** nêu rõ không bắt buộc câu xin lỗi khi đơn được chấp nhận hoàn tiền. |
| 5 | `H-051` (`tone_ok`) | `FAIL` | `PASS` | Người đúng | `"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."` — Dùng từ `"refund"` được CS LogiX cho phép; judge phạt vì lẫn tiếng Anh. **Sửa rubric:** whitelist thuật ngữ nghiệp vụ cho phép (`refund`, `LogiX`). |
| 6 | `H-063` (`tone_ok`) | `PASS` | `FAIL` | Người đúng | `"Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ."` — Hứa hẹn `"sẽ hoàn thêm"` sai sự thật/ngoài kết quả hệ thống. **Sửa rubric:** đưa cam kết ngoài kết quả ledger vào lỗi nghiêm trọng (`FAIL`). |
| 7 | `H-070` (`tone_ok`) | `PASS` | `FAIL` | Người đúng | `"Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂"` — Emoji cười cợt không phù hợp ngữ cảnh khiếu nại. **Sửa rubric:** cấm emoji giải trí trong phản hồi CSKH. |
| 8 | `H-081` (`tone_ok`) | `FAIL` | `PASS` | **Judge đúng** | `"Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ."` — Nhãn người bị sai do annotator đọc nhầm ticket (`FP` thực chất là lỗi gán nhãn). **Hành động:** cập nhật nhãn ground truth và rà soát chéo 2 người gán nhãn độc lập. |
| 9 | `H-088` (`tone_ok`) | `FAIL` | `PASS` | Người đúng | `"Dạ, dạ, LogiX đã hoàn 40.000đ cho đơn O-233 ạ."` — Lặp từ `"Dạ"` do lỗi gõ nhỏ nhưng vẫn lịch sự; **Sửa rubric:** không đánh FAIL tone chỉ vì lặp 1 từ lịch sự. |
| 10 | `H-094` (`tone_ok`) | `FAIL` | `FAIL` (H=FAIL, J=PASS) | Người đúng | `"Da, LogiX da hoan 40.000đ cho don O-341, xin loi vi su bat tien."` — Tiếng Việt mất dấu toàn bộ; judge chấm `PASS`. **Sửa rubric:** bắt buộc có dấu tiếng Việt chuẩn. |
| 11 | `HL-015`, `HL-016`, `HL-028`… (`helpful`) | `PASS` | `FAIL` | Người đúng | `"Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ."` (ledger chỉ ghi `40.000đ`). Judge bị đánh lừa bởi giọng văn xin lỗi dài dòng/lịch sự (`FN = 21` gồm 18 ca sai tiền FM-08 + 3 ca sai xưng hô `HL-047`, `HL-091`, `HL-097`). **Hành động:** không dùng LLM judge cho tính đúng số tiền; thay bằng code grader `ReplyMatchesLedger`. |

## Kết luận

- **`tone_ok` (n=100, TP=24, FP=4, FN=6, TN=66):** Đạt cả 3 ngưỡng FLOORS (`κ = 0.757 ≥ 0.6`, `Precision = 0.857 ≥ 0.8`, `Recall = 0.800 ≥ 0.7`). Observed fail rate `0.28`, sau hiệu chỉnh Rogan–Gladen đạt `0.30` (khớp với tỉ lệ lỗi thật của người gán nhãn `30/100`). Có thể dùng `tone_ok` làm tín hiệu đánh giá giọng văn sau khi cập nhật rubric như trên.
- **`helpful` (n=100, TP=9, FP=0, FN=21, TN=70):** **Bị loại hoàn toàn khỏi release gate** vì `Recall = 0.30 < 0.70` và `κ = 0.375 < 0.60`. Tuy `Precision = 1.0` (không báo nhầm), judge chỉ phát hiện được `9/30` ca lỗi (các câu trả lời cộc lốc/lạc đề như `HL-001`, `HL-003`, `HL-019`) và **bỏ lọt 21/30 ca (`70%`)**, chủ yếu là các câu trả lời khéo léo nhưng **nói sai số tiền hoàn so với ledger** (`18` ca) và sai xưng hô (`3` ca). Do đó observed fail rate chỉ là `0.09`, làm ẩn phần lớn lỗi thực tế (`0.30`).
- **Quy tắc áp dụng:** Tiền và phê duyệt luôn kiểm bằng **code** (`RefundAmountCorrect`, `ApprovalBypass`, `ReplyMatchesLedger`), không bao giờ giao cho LLM judge.
- **Rủi ro còn lại:** Judge chỉ được kiểm trên dữ liệu replay đã công khai (`judge_tone_public.csv`, `judge_helpful_public.csv`); cần thu thập thêm nhãn người mới trên tập held-out thật trước khi áp dụng judge `tone_ok` cho production.
