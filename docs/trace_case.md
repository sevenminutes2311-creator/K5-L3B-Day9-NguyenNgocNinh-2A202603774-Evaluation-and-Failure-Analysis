# Trace case: từ trace tới quyết định sai đầu tiên

> Ghi nhận trên shape lỗi `seeded_regression` (đối chứng với `fixed`) trước khi sinh report cuối cùng; mọi bước đều dẫn số thứ tự event từ `python -m lab9.trace_case`.

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (đối chiếu thêm trên `swarm C-002@55`, run ID `R-seeded_regression-C-002-s11` / `R-swarm-C-002-s55`) |
| Triệu chứng | `TrialPass` FAIL (`status resolved != denied`); `RefundAmountCorrect` FAIL (`ledger=20000 != label=0`); `DbFactKept` FAIL (`1 override event(s)`). Reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."` và ledger ghi `refund_vnd = 20000`, `refund_count = 1`, trong khi label yêu cầu `status = denied`, `refund_vnd = 0`. |
| Bước sai đầu tiên | Event **3** `model_override`: `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event **1** (`handoff`) thiết lập đúng phạm vi `owner_order_only` và `allowed_tools`; Event **2** (`investigator`) truy vấn DB `orders` chính xác cho đơn `O-202` với `delay_days = 2` (chưa đủ ngưỡng tối thiểu 3 ngày của `SHIP-LATE-03`). Đến Event **3** (`model_override`), agent lại tin con số `"trễ 5 ngày"` từ ticket để ghi đè `delay_days = 2` của DB, kéo theo Event **4** (`quote`) tính nhầm `amount_vnd = 20000` và ghi hoàn tiền sai vào ledger. |
| Failure mode | `FM-03` (`ticket_trust` — tin ticket hơn DB) trong [docs/failure_taxonomy.md](failure_taxonomy.md) |
| Đối chứng | Trên `fixed C-002@11` (`TrialPass: PASS (ok)`): Event 1 (`handoff`) và Event 2 (`investigator`, `delay_days=2`) giống hệt, **không có** event `model_override`; Event 3 (`quote`) trả `{"amount_vnd": 0, "reason": "no_entitlement", "clause_ids": [], "parts": {}}`; Event 4 (`reply`) từ chối đúng (`status = denied`, `refund_vnd = 0`). |
| Regression test | `test_c002_seed11_seeded_regression_is_caught_by_graders` và `test_c002_seed11_fixed_passes_and_keeps_db_fact` trong [src/tests/test_lab9_trace_case.py](../src/tests/test_lab9_trace_case.py) — assert qua `DbFactKept`, `RefundAmountCorrect` và `TrialPass`; đã thấy bắt lỗi trên `seeded_regression` và pass trên `fixed`. |
| Chưa chắc chắn | `MockLLM` mô phỏng quyết định parse/override theo rule và seed (`seed % 5 == 0` trên `swarm`); trên LLM thật ở môi trường production, tỉ lệ bị đánh lừa bởi số liệu giả trong ticket (prompt injection / thuyết phục bằng lời) cần được đo thêm trên tập dữ liệu người dùng thực. |
