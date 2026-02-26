Quantix AI Serverless - System Structure (Serverless Edition)
🎯 Mục tiêu
Xây dựng một hệ thống phân tích và giao dịch tự động cho một cặp tiền EUR/USD trên khung M15, sử dụng dữ liệu từ Twelve Data (free plan) , với khả năng:

Dễ dàng thử nghiệm các mô hình phân tích khác nhau (EMA/RSI, Smart Money Concepts, …).

Tự động học (self-learning) để chọn mô hình và tham số tốt nhất dựa trên kết quả lịch sử.

Giám sát trạng thái tín hiệu theo thời gian thực (mỗi phút).

Dashboard trực quan hiển thị tín hiệu, hiệu suất các mô hình, và nhật ký hệ thống.

Vận hành hoàn toàn miễn phí, không cần quản lý máy chủ (serverless).

🏗️ Kiến trúc tổng thể
Hệ thống được xây dựng dựa trên các dịch vụ serverless và lưu trữ đám mây:

GitHub Actions – Chạy các tác vụ định kỳ (phân tích mỗi 15 phút, tự động học mỗi ngày).

Google Sheets – Đóng vai trò cơ sở dữ liệu (lưu tín hiệu, kết quả, cấu hình, nhật ký).

Google Apps Script – Theo dõi trạng thái tín hiệu theo thời gian thực (mỗi phút) và gửi thông báo Telegram.

Twelve Data API – Cung cấp dữ liệu giá lịch sử và giá hiện tại.

Telegram Bot – Gửi thông báo khi có tín hiệu mới, vào lệnh, đóng lệnh.

Google Sheets (Dashboard) – Tự động cập nhật các bảng tổng hợp, biểu đồ để theo dõi hệ thống.

Sơ đồ tương tác

graph TD
    subgraph "GitHub Actions"
        A[Analyzer Workflow<br>Mỗi 15 phút]
        L[Self-Learning Workflow<br>Mỗi ngày]
    end

    subgraph "Google Sheets"
        DB[(Signals<br>Model Results<br>Config<br>Logs)]
    end

    subgraph "Apps Script"
        W[Watcher Trigger<br>Mỗi phút]
        D[Web App Dashboard<br>Tùy chọn]
    end

    subgraph "External"
        TD[Twelve Data API]
        TG[Telegram Bot]
    end

    A -->|Lấy dữ liệu| TD
    A -->|Ghi tín hiệu mới| DB
    A -->|Ghi log| DB

    L -->|Đọc kết quả lịch sử| DB
    L -->|Tính toán và chọn model tốt nhất| DB
    L -->|Cập nhật cấu hình| DB

    W -->|Đọc tín hiệu active| DB
    W -->|Lấy giá realtime| TD
    W -->|Cập nhật trạng thái| DB
    W -->|Gửi thông báo| TG
    W -->|Ghi log| DB

    D -->|Đọc dữ liệu hiển thị| DB
    D -->|Hiển thị dashboard| Người dùng




🧩 Các thành phần chi tiết
1. GitHub Actions – Analyzer Workflow
Tần suất: Mỗi 15 phút (cron */15 * * * *).

Chức năng:

Đọc cấu hình từ Google Sheets (model hiện đang active, tham số).

Lấy 100 nến M15 mới nhất của EUR/USD từ Twelve Data.

Gọi phương thức analyze() của model tương ứng (EMA/RSI, SMC, …).

Nếu có tín hiệu, ghi vào sheet signals và sheet model_results (kèm thông tin model, tham số, độ tin cậy).

Ghi nhật ký vào sheet logs.

Mã nguồn: .github/workflows/analyzer.yml + analyze.py

2. GitHub Actions – Self-Learning Workflow
Tần suất: Mỗi ngày lúc 00:00 UTC (cron 0 0 * * *).

Chức năng:

Đọc tất cả tín hiệu đã đóng (có kết quả win/loss) từ sheet model_results.

Nhóm theo model và tham số (lưu dưới dạng JSON).

Tính win rate, profit factor, số lượng mẫu cho mỗi nhóm.

Chọn ra bộ model + tham số tốt nhất (ví dụ: win rate cao nhất, tối thiểu 10 mẫu).

Cập nhật cấu hình (sheet config) để analyzer sử dụng từ ngày hôm sau.

Ghi nhật ký và gửi thông báo Telegram về sự thay đổi.

Mã nguồn: .github/workflows/self_learn.yml + self_learn.py

3. Google Apps Script – Watcher
Trigger: Time-driven, mỗi phút.

Chức năng:

Đọc tất cả tín hiệu có trạng thái WAITING_FOR_ENTRY hoặc ENTRY_HIT từ sheet signals.

Lấy giá hiện tại của EUR/USD từ Twelve Data (API price).

Với mỗi tín hiệu WAITING_FOR_ENTRY: kiểm tra nếu giá chạm entry → chuyển sang ENTRY_HIT, ghi thời gian, gửi Telegram.

Với mỗi tín hiệu ENTRY_HIT: kiểm tra chạm TP/SL hoặc quá 90 phút → cập nhật trạng thái (CLOSED_WIN/CLOSED_LOSS/EXPIRED), ghi thời gian đóng, gửi Telegram.

Sử dụng LockService để tránh xung đột khi nhiều trigger chạy cùng lúc.

Mã nguồn: Tập tin watcher.gs trong Apps Script.

4. Google Sheets – Database
Sheet config:

Lưu cấu hình hệ thống: active_model (tên model hiện dùng), models (danh sách các model và tham số mặc định), last_updated, ...

Sheet signals:

Các cột: ID, Timestamp, Pair, Direction, Entry, TP, SL, State, CreatedAt, UpdatedAt, EntryTime, CloseTime, Notes.

Lưu các tín hiệu được sinh ra, phục vụ theo dõi và dashboard.

Sheet model_results:

Các cột: ID, Timestamp, ModelName, Direction, Entry, TP, SL, Confidence, Params (JSON), State, ClosedAt, Outcome (win/loss), Notes.

Lưu chi tiết mỗi tín hiệu kèm thông tin model, phục vụ self-learning.

Sheet logs:

Các cột: Timestamp, Message.

Ghi lại nhật ký hoạt động của toàn bộ hệ thống (analyzer, watcher, self-learning).

Sheet dashboard_data (tự động tổng hợp từ các sheet khác bằng công thức Google Sheets):

Ví dụ: số tín hiệu theo model, win rate gần đây, tín hiệu đang active, …

5. Dashboard – Giao diện giám sát
Có hai phương án triển khai dashboard:

Phương án A: Google Sheets làm dashboard (khuyên dùng)
Tận dụng các sheet đã có, tạo thêm các sheet Dashboard_Summary, Dashboard_ActiveSignals, Dashboard_Performance.

Dùng các hàm Google Sheets như QUERY, FILTER, SPARKLINE, GOOGLEFINANCE để tạo biểu đồ và bảng tổng hợp tự động cập nhật.

Có thể thêm các nút bấm (chạy Apps Script) để làm mới dữ liệu hoặc thực hiện tác vụ thủ công.

Phương án B: Web App bằng Apps Script (nâng cao)
Xây dựng một ứng dụng web đơn giản bằng HtmlService trong Apps Script, đọc dữ liệu từ các sheet và hiển thị dưới dạng bảng, biểu đồ (Chart.js).

Triển khai dưới dạng web app, có thể share cho nhiều người xem.

Nội dung dashboard tối thiểu:

Tín hiệu hiện tại: Danh sách các tín hiệu WAITING_FOR_ENTRY và ENTRY_HIT.

Lịch sử gần đây: 20 tín hiệu gần nhất, kèm kết quả.

Hiệu suất model: Win rate 7 ngày qua, tổng số tín hiệu, profit factor (ước lượng).

Nhật ký hệ thống: 20 dòng log gần nhất.

Trạng thái API: Số request Twelve Data đã dùng trong ngày (nếu có thể).

6. Thư viện dùng chung (utils)
sheets.py: Các hàm đọc/ghi Google Sheets (dùng cho GitHub Actions).

twelve.py: Lấy dữ liệu từ Twelve Data (giá lịch sử, giá hiện tại).

telegram.py: Gửi thông báo Telegram.

models/base.py: Lớp cơ sở cho tất cả các model.

📁 Cấu trúc repository (GitHub)
text
Quantix_AI_Core/
├── .github/
│   └── workflows/
│       ├── analyzer.yml          # Workflow chạy phân tích
│       └── self_learn.yml        # Workflow tự động học
├── models/
│   ├── __init__.py
│   ├── base.py                   # Abstract base class
│   ├── ema_rsi.py                # Model EMA + RSI
│   ├── smc.py                     # Model Smart Money Concepts
│   └── ...                        # Các model khác
├── utils/
│   ├── sheets.py                  # Tương tác Google Sheets
│   ├── twelve.py                  # Lấy dữ liệu từ Twelve Data
│   ├── telegram.py                 # Gửi Telegram
│   └── logger.py                   # Ghi log xuống sheet
├── analyze.py                      # Script chính cho analyzer
├── self_learn.py                   # Script cho self-learning
├── requirements.txt                # Thư viện Python cần thiết
├── config.example.yaml             # Mẫu cấu hình
└── README.md                       # Hướng dẫn thiết lập
Giải thích các file quan trọng:
models/base.py: Định nghĩa lớp TradingModel với các phương thức trừu tượng analyze() và get_params().

models/ema_rsi.py: Cài đặt cụ thể, dùng EMA và RSI để sinh tín hiệu.

models/smc.py: Cài đặt theo Smart Money Concepts (xác định xu hướng, order block, FVG).

utils/sheets.py: Xử lý xác thực và các thao tác đọc/ghi Google Sheets (dùng service account).

analyze.py:

Đọc cấu hình từ Google Sheets (hoặc file config).

Chọn model tương ứng, gọi analyze().

Ghi kết quả vào sheets.

self_learn.py:

Đọc dữ liệu từ model_results.

Tính toán và chọn model tốt nhất.

Ghi cập nhật vào sheet config.

🔁 Luồng hoạt động chi tiết
1. Luồng Analyzer (Mỗi 15 phút)
GitHub Actions kích hoạt workflow.

Script analyze.py chạy:

Lấy cấu hình từ sheet config (model active + tham số).

Khởi tạo model tương ứng.

Gọi Twelve Data lấy 100 nến M15.

Gọi model.analyze(df), nhận tín hiệu (hoặc None).

Nếu có tín hiệu:

Ghi vào sheet signals.

Ghi vào sheet model_results (kèm params, confidence).

Ghi log vào sheet logs.

2. Luồng Watcher (Mỗi phút)
Apps Script trigger chạy checkSignals().

Lấy danh sách tín hiệu active (state = WAITING_FOR_ENTRY hoặc ENTRY_HIT).

Gọi Twelve Data lấy giá hiện tại.

Duyệt từng tín hiệu:

Nếu WAITING_FOR_ENTRY: kiểm tra entry → nếu hit, cập nhật thành ENTRY_HIT, gửi Telegram.

Nếu ENTRY_HIT: kiểm tra TP/SL/timeout → cập nhật trạng thái cuối, gửi Telegram.

Ghi log.

3. Luồng Self-Learning (Mỗi ngày)
GitHub Actions kích hoạt workflow.

Script self_learn.py chạy:

Đọc toàn bộ dữ liệu từ model_results.

Lọc các tín hiệu đã đóng (có outcome).

Nhóm theo model và params, tính win rate, số mẫu.

Chọn bộ tốt nhất (đủ số mẫu tối thiểu, win rate cao nhất).

Cập nhật vào sheet config (cột active_model và params).

Gửi Telegram thông báo model mới được chọn.

Ghi log.

📡 Tích hợp dữ liệu
Twelve Data API
Lấy dữ liệu lịch sử: https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=15min&outputsize=100&apikey={KEY}

Lấy giá hiện tại: https://api.twelvedata.com/price?symbol=EUR/USD&apikey={KEY}

Giới hạn free: 800 requests/ngày. Cần theo dõi và tiết chế:

Analyzer: 4 lần/giờ × 24 = 96 requests/ngày (cố định).

Watcher: mỗi phút gọi 1 lần nếu có tín hiệu active. Tối đa 1440 requests/ngày nếu luôn có tín hiệu. Để đảm bảo không vượt quota, watcher chỉ gọi giá một lần cho mỗi lần chạy (dùng chung cho tất cả tín hiệu). Nếu không có tín hiệu active, không gọi API. Với tần suất tín hiệu thực tế (vài lần/ngày), lượng request vẫn dưới 800.

Google Sheets API
Sử dụng service account để xác thực từ GitHub Actions.

Apps Script dùng quyền của người dùng (đã ủy quyền khi cài trigger).

Telegram Bot
Gửi thông báo qua HTTP POST tới https://api.telegram.org/bot{TOKEN}/sendMessage.

📊 Dashboard cụ thể
Sheet "Dashboard_Overview"
Thành phần	Hiển thị
Tín hiệu đang active	Bảng lọc từ signals với state WAITING_FOR_ENTRY hoặc ENTRY_HIT (ID, hướng, entry, TP, SL, thời gian)
Thống kê nhanh	- Tổng tín hiệu hôm nay
- Win rate 7 ngày qua
- Model đang dùng
Biểu đồ hiệu suất model	Cột win rate theo model (dùng SPARKLINE hoặc biểu đồ cột)
20 tín hiệu gần nhất	ID, thời gian, model, hướng, kết quả
Nhật ký hệ thống	10 dòng log mới nhất từ sheet logs
Sheet "Model_Performance" (chi tiết)
Dùng QUERY để tổng hợp win rate, số lượng theo model và theo tháng.

Cập nhật tự động
Tất cả các bảng trên đều dùng công thức Google Sheets, tự động cập nhật khi dữ liệu nguồn thay đổi.

Có thể thêm một nút "Refresh" chạy Apps Script để làm mới các công thức nếu cần.

🔧 Khả năng mở rộng
Thêm model mới
Tạo file models/new_model.py, kế thừa TradingModel.

Định nghĩa analyze() và get_params().

Thêm tên model vào cấu hình (sheet config hoặc file).

(Tùy chọn) Thêm tham số mặc định vào config.

Thêm cặp tiền mới
Hiện tại hệ thống chỉ theo dõi 1 cặp. Để mở rộng, cần:

Sửa các script để nhận danh sách cặp từ config.

Điều chỉnh cấu trúc sheet để có cột Pair.

Đảm bảo quota Twelve Data vẫn đủ (nhân lên theo số cặp).

Nâng cấp self-learning
Thay vì chọn model tốt nhất tuyệt đối, có thể dùng ensemble: kết hợp nhiều model, mỗi model có trọng số dựa trên win rate.

Lưu lại lịch sử các lần chọn model để phân tích sau.

🛡️ Bảo mật và giới hạn
GitHub Secrets: Lưu TWELVE_API_KEY, GOOGLE_CREDS (JSON của service account), SPREADSHEET_ID, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID.

Google Sheets: Chia sẻ sheet với email service account (quyền Editor). Không chia sẻ công khai.

Apps Script: Sử dụng PropertiesService để lưu token, tránh hardcode.

Twelve Data free: Cần theo dõi sát lượng request, có thể giảm tần suất watcher xuống 2 phút nếu cần.

📈 Kết luận
Hệ thống này cung cấp một nền tảng hoàn chỉnh, miễn phí, dễ mở rộng để thử nghiệm các chiến lược giao dịch tự động trên EUR/USD M15. Với kiến trúc tách biệt rõ ràng, bạn có thể:

Tập trung phát triển các mô hình mới mà không lo ảnh hưởng phần còn lại.

Dùng dashboard để giám sát và đánh giá hiệu quả các mô hình theo thời gian thực.

Tận dụng sức mạnh của Google Sheets cho việc lưu trữ và trực quan hóa.