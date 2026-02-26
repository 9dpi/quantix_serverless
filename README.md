# 🤖 Quantix AI Serverless Trading System

Hệ thống giao dịch tự động hóa 100% hoạt động dựa trên cấu trúc Serverless (GitHub Actions + Google Sheets + Apps Script). Hệ thống tự động phân tích kỹ thuật, phát tín hiệu (Signals) và giám sát giá thị trường để chốt lời/cắt lỗ tự động.

## 🌟 Tính năng
- **Serverless Architecture**: 0đ chi phí vận hành (Free Tier của GitHub & Google).
- **AI Analysis**: Tự động chạy mỗi 30 phút trên GitHub Actions.
- **Real-time Monitoring**: Apps Script Watcher theo dõi giá mỗi phút để tự động đóng lệnh.
- **Multi-source Data**: Tự động chuyển đổi giữa Binance API và Yahoo Finance để đảm bảo dữ liệu không bị gián đoạn.
- **Terminal Dashboard**: Giao diện Dashboard phong cách Matrix cổ điển, hỗ trợ Responsive hoàn hảo cho Mobile.
- **Instant Notification**: Nhận báo cáo tín hiệu ngay lập tức qua Telegram Bot.

## 🏗️ Kiến trúc hệ thống
1. **GitHub Actions**: Bộ não phân tích (Python).
2. **Google Sheets**: Cơ sở dữ liệu trung tâm lưu trữ Config, Signals & Logs.
3. **Google Apps Script**: Cổng kết nối dữ liệu (API) và bộ máy giám sát giám thực tế (Watcher).
4. **GitHub Pages**: Giao diện Dashboard hiển thị trạng thái hệ thống.

## 🔒 Cơ chế bảo mật
Để đảm bảo an toàn khi đưa mã nguồn lên môi trường công cộng (GitHub):

1. **Environment Variables**: Toàn bộ thông tin nhạy cảm (API Keys, Credential JSON) được lưu trữ tại **GitHub Secrets**. Tuyệt đối không hardcode trong mã nguồn.
2. **.gitignore**: Đã cấu hình để loại bỏ các file `.json`, `.env` và thư mục rác. File Service Account của Google sẽ không bao giờ bị đẩy lên GitHub.
3. **Apps Script Properties**: Token Telegram được lưu trong `ScriptProperties`, không hiển thị trong mã nguồn Script công khai.
4. **Obfuscation**: Các URL nhạy cảm của Web App được quản lý tập trung và chỉ cho phép truy cập theo phương thức quy định.

## 🚀 Hướng dẫn cài đặt

### 1. Chuẩn bị Google Sheet
- Tạo Google Sheet mới.
- Chạy file `setup_sheets.py` cục bộ để khởi tạo cấu trúc các tab chuẩn.
- Lấy `SHEET_ID` từ URL của trình duyệt.
- Tạo file Service Account (JSON) từ Google Cloud Console và cấp quyền Editor cho Email của Service Account vào Sheet.

### 2. Cấu hình GitHub Secrets
Truy cập kho code trên GitHub -> **Settings** -> **Secrets and variables** -> **Actions**, thêm các Secrets sau:
- `GOOGLE_CREDS`: Nội dung file JSON của Service Account.
- `SHEET_ID`: ID của Google Sheet.
- `TELE_TOKEN`: Token của Telegram Bot.
- `TELE_CHAT_ID`: Chat ID của bạn.

### 3. Triển khai Apps Script
- Truy cập Google Sheet -> **Extensions** -> **Apps Script**.
- Copy nội dung file `watcher.gs` và `dashboard/Code.gs` vào.
- Thiết lập Trigger cho hàm `watchSignals` chạy mỗi 1 phút.
- Triển khai dưới dạng **Web App** (Deploy as Web App), chọn quyền truy cập là "Anyone".

### 4. Kích hoạt Dashboard
- Vào **Settings** -> **Pages** trên GitHub.
- Chọn nguồn là thư mục `main` (hoặc thư mục `dashboard` tùy cấu trúc).
- Hệ thống sẽ cấp cho bạn một link Dashboard công khai.

## 📝 Giấy phép
Hệ thống này được phát triển phục vụ mục đích học tập và nghiên cứu. Người dùng chịu hoàn toàn trách nhiệm về rủi ro tài chính khi sử dụng trong giao dịch thực tế.

---
*Developed by Antigravity AI @ 2026*
