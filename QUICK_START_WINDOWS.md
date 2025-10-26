# 🚀 QUICK START - Windows

## 📦 Bước 1: Tải và Giải Nén

1. Download file: `tradex-kyc-platform.zip` (662KB)
2. Giải nén vào thư mục bạn muốn (ví dụ: `C:\Projects\trading-platform\`)

## ⚡ Bước 2: Cài Đặt Nhanh (Lần Đầu)

### Cài đặt phần mềm cần thiết:
1. **Python 3.11+**: https://www.python.org/downloads/
   - ✅ Nhớ tick "Add Python to PATH"
2. **Node.js LTS**: https://nodejs.org/
3. **MongoDB**: https://www.mongodb.com/try/download/community

### Chạy file setup tự động:
```cmd
Double-click: setup.bat
```

Script này sẽ tự động:
- ✅ Tạo Python virtual environment
- ✅ Cài đặt backend dependencies
- ✅ Cài đặt frontend dependencies
- ✅ Tạo MongoDB data directory

## 🎯 Bước 3: Chạy Ứng Dụng

### Cách 1: Chạy Tất Cả Cùng Lúc (Khuyến Nghị)
```cmd
Double-click: start-all.bat
```

### Cách 2: Chạy Riêng Từng Service

**Terminal 1 - Backend:**
```cmd
Double-click: start-backend.bat
```

**Terminal 2 - Frontend:**
```cmd
Double-click: start-frontend.bat
```

## 🌐 Bước 4: Truy Cập

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

### Đăng nhập Admin:
```
Email:    admin@trading.com
Password: Admin@123456
```

---

## 📂 Files Trong ZIP

```
tradex-platform/
├── setup.bat                          ⚡ Setup tự động (chạy lần đầu)
├── start-all.bat                      🚀 Start tất cả services
├── start-backend.bat                  🔧 Start backend only
├── start-frontend.bat                 🎨 Start frontend only
├── HƯỚNG_DẪN_CHẠY_TRÊN_WINDOWS.md    📚 Hướng dẫn chi tiết
├── HƯỚNG_DẪN_SỬ_DỤNG.md             📖 Hướng dẫn sử dụng
├── README.md                          📄 Quick reference
├── backend/                           
│   ├── server.py                      🐍 FastAPI server
│   ├── telegram_service.py            📱 Telegram integration
│   ├── requirements.txt               📦 Python dependencies
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── pages/admin/AdminKYC.js   🔐 KYC management
│   │   └── components/VerifiedBadge.js ✅ Blue badge
│   ├── package.json                   📦 Node dependencies
│   └── ...
└── test_result.md                     📊 Testing history
```

---

## ⚠️ Lỗi Thường Gặp & Giải Pháp

### ❌ "MongoDB connection failed"
**Giải pháp:**
```cmd
# Mở Services (Win + R → services.msc)
# Tìm "MongoDB Server" → Start
```

### ❌ "Port 8001 already in use"
**Giải pháp:**
```cmd
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### ❌ "python is not recognized"
**Giải pháp:**
- Cài lại Python và tick "Add Python to PATH"
- Hoặc dùng: `py` thay vì `python`

### ❌ "Backend không connect được"
**Giải pháp:**
- Kiểm tra file `frontend\.env`:
  ```
  REACT_APP_BACKEND_URL=http://localhost:8001
  ```
- Restart frontend sau khi sửa .env

---

## 📚 Chi Tiết Hơn

Xem file: **`HƯỚNG_DẪN_CHẠY_TRÊN_WINDOWS.md`** để có:
- ✅ Hướng dẫn cài đặt từng bước chi tiết
- ✅ Giải quyết tất cả lỗi có thể gặp
- ✅ Tips & tricks
- ✅ Production deployment
- ✅ Debugging guide

---

## 🎯 Workflow Hàng Ngày

### Bắt đầu:
1. Double-click `start-all.bat`
2. Đợi 10 giây cho backend khởi động
3. Browser tự động mở http://localhost:3000
4. Login với admin@trading.com / Admin@123456

### Kết thúc:
1. `Ctrl + C` trong cửa sổ Backend
2. `Ctrl + C` trong cửa sổ Frontend
3. Done!

---

## ✨ Tính Năng KYC

1. **Upload ảnh lên Telegram Bot**
   - Telegram Token và Chat ID đã được cấu hình sẵn
   
2. **Admin duyệt KYC**
   - Vào menu KYC → Xem pending submissions
   - Click vào submission → View 3 images
   - Approve/Reject
   
3. **Verified Badge**
   - Badge xanh lam (✓) xuất hiện khi user verified
   - Hiển thị ở User list, Dashboard, Profile

---

## 🆘 Cần Giúp Đỡ?

1. **Xem logs:**
   - Backend: Trong terminal window
   - Frontend: Browser console (F12)
   
2. **Kiểm tra services:**
   ```cmd
   # MongoDB
   mongosh
   
   # Backend
   curl http://localhost:8001/api/
   
   # Frontend
   # Mở browser: http://localhost:3000
   ```

3. **Reset everything:**
   ```cmd
   # Backend
   cd backend
   rd /s /q venv
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   rd /s /q node_modules
   yarn install
   ```

---

## 🎉 Hoàn Tất!

Sau khi setup, bạn có:
- ✅ Backend chạy trên port 8001
- ✅ Frontend chạy trên port 3000
- ✅ MongoDB lưu dữ liệu
- ✅ KYC system với Telegram Bot
- ✅ Admin panel hoàn chỉnh

**Happy Coding!** 🚀

---

## 📞 Support Files

- **Chi tiết**: `HƯỚNG_DẪN_CHẠY_TRÊN_WINDOWS.md`
- **Tính năng**: `HƯỚNG_DẪN_SỬ_DỤNG.md`
- **API Docs**: http://localhost:8001/docs (khi server chạy)
