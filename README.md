# AuraFinance - Intelligent Personal Finance Dashboard

Dự án full-stack **AuraFinance** kết hợp giữa **FastAPI (Backend)** và **Vue 3 (Frontend)**. Đây là một đồ án được thiết kế chuẩn doanh nghiệp nhằm gây ấn tượng mạnh với nhà tuyển dụng trong các buổi phỏng vấn.

---

## 🚀 Các Tính Năng Nổi Bật (Interview Highlights)

1.  **Kiến trúc Chuẩn Doanh nghiệp**:
    *   **Backend**: Chia tầng rõ ràng gồm **MVC** kết hợp với **Service Layer** và **Repository Pattern** nhằm cô lập business logic và dễ dàng viết unit tests.
    *   **Frontend**: Áp dụng mô hình **MVVM** với **Composition API** (`<script setup>`) và quản lý state tập trung bằng **Pinia**.
2.  **Thông báo Thời gian thực (Real-time WebSockets)**:
    *   Sử dụng kết nối WebSocket để đẩy thông báo lập tức lên màn hình (ví dụ: cảnh báo thâm hụt ngân sách khi chạm ngưỡng 80% hoặc 100% hạn mức).
3.  **Tự động hóa Giao dịch Định kỳ (Background Workers)**:
    *   Sử dụng cơ chế `lifespan` và `asyncio` worker ngầm trong FastAPI để tự động ghi nhận các khoản thu/chi định kỳ (hàng ngày, hàng tuần, hàng tháng).
4.  **Trợ lý Phân tích tài chính AI (Rule-based)**:
    *   Phân tích hành vi tiêu dùng và đưa ra lời khuyên tài chính thông minh dựa trên lịch sử chi tiêu thực tế.
5.  **Xuất báo cáo CSV**:
    *   Hỗ trợ tải xuống lịch sử giao dịch dưới dạng file CSV chuẩn UTF-8 (mở được trực tiếp trên Excel không lỗi font tiếng Việt).
6.  **Giao diện Glassmorphism Premium**:
    *   Giao diện Dark Mode cao cấp được thiết kế thủ công bằng **Tailwind CSS v3** kết hợp đồ thị trực quan sinh động từ **ApexCharts**.

---

## 🛠️ Cài đặt & Khởi chạy dự án

### 1. Khởi chạy Backend (FastAPI)

Yêu cầu máy cài sẵn Python 3.10+.

```bash
# Di chuyển vào thư mục backend
cd backend

# Kích hoạt môi trường ảo
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate

# Cài đặt dependencies (đã được cài đặt sẵn qua script setup.bat)
pip install -r requirements.txt

# Khởi chạy server
uvicorn app.main:app --reload
```

Server backend sẽ khởi chạy tại: `http://127.0.0.1:8000`
Tài liệu API tương tác tự động (Swagger UI): `http://127.0.0.1:8000/docs`

---

### 2. Khởi chạy Frontend (Vue 3 + Vite)

Yêu cầu máy cài sẵn Node.js 18+.

```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies (đã được cài đặt sẵn qua script setup.bat)
npm install

# Khởi chạy dev server
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:5173`

---

## 📁 Cấu trúc Thư mục Dự án

```text
AuraFinance/
├── backend/
│   ├── app/
│   │   ├── api/            # API Controllers (Routers)
│   │   ├── core/           # Config, database connection, JWT security
│   │   ├── models/         # SQLAlchemy Models (User, Transaction, Budget, Recurring)
│   │   ├── repositories/   # Tầng truy vấn cơ sở dữ liệu (Generic Repository Pattern)
│   │   ├── schemas/        # Pydantic Schemas (Data validation)
│   │   ├── services/       # Tầng nghiệp vụ chính (Auth, Transaction, Budget, AI, Report)
│   │   └── main.py         # Entrypoint chính của FastAPI
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/     # Các components tái sử dụng
│   │   ├── views/          # Các trang giao diện (Dashboard, Transactions, Budgets, Recurring, Login)
│   │   ├── router/         # Vue Router (có Navigation Guard kiểm tra Auth)
│   │   ├── stores/         # Pinia Stores (Quản lý trạng thái toàn cục)
│   │   ├── services/       # Axios API Client
│   │   ├── style.css       # Custom glassmorphic CSS & Tailwind directives
│   │   └── main.js         # Entrypoint khởi tạo Vue app
│   ├── tailwind.config.js  # Cấu hình Tailwind CSS
│   └── package.json
│
├── setup.bat               # File script setup nhanh dự án
├── ke_hoach.md             # Kế hoạch phát triển chi tiết
└── tien_do.md              # File theo dõi tiến độ dự án
```
