# AuraFinance - Quản lý tài chính cá nhân

Web app quản lý thu chi cá nhân, theo dõi ngân sách, giao dịch định kỳ, và xuất báo cáo.

## Công nghệ

- **Frontend**: Vue 3, Pinia, Vue Router, Tailwind CSS, ApexCharts, Axios
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL (SQLite cho dev), JWT, WebSocket
- **AI**: Hỗ trợ nhiều provider (Gemini, OpenAI, Claude, DeepSeek...)

## Tính năng

- Dashboard tổng quan thu/chi, biểu đồ tròn, điểm thưởng
- Nhật ký giao dịch (thêm, sửa, xóa)
- Hạn mức chi tiêu theo danh mục
- Giao dịch định kỳ tự động
- Báo cáo CSV, tổng kết theo năm
- Trò chuyện với AI phân tích tài chính
- Thông báo real-time qua WebSocket
- Khoá màn hình, widget thời tiết, lịch âm dương
- Nhạc nền (tải file MP3 hoặc nhập link)

## Chạy thử

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs tại `http://127.0.0.1:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Mở `http://localhost:5173`

## Môi trường

Copy `.env.example` thành `.env` và điền các biến môi trường cần thiết.

Tài khoản demo: `demo@aurafinance.app` / `123456` (chạy ở chế độ development)
