# 🪟 Hướng Dẫn Chạy Project Trên Windows

## 📋 Yêu Cầu Hệ Thống

### 1. Cài Đặt Phần Mềm Cần Thiết

#### Python 3.11+
```
Tải về: https://www.python.org/downloads/
✅ Chọn "Add Python to PATH" khi cài đặt
```

#### Node.js 16+ và npm
```
Tải về: https://nodejs.org/
Khuyến nghị: Phiên bản LTS (Long Term Support)
```

#### MongoDB Community Edition
```
Tải về: https://www.mongodb.com/try/download/community
Chọn: Windows x64 MSI
```

#### Yarn (Package Manager)
```
Sau khi cài Node.js, mở Command Prompt/PowerShell:
npm install -g yarn
```

---

## 🚀 Các Bước Cài Đặt

### Bước 1: Giải Nén File ZIP

1. Giải nén file `tradex-kyc-platform.zip` vào thư mục bạn muốn, ví dụ:
   ```
   C:\Projects\tradex-platform\
   ```

2. Cấu trúc thư mục sau khi giải nén:
   ```
   tradex-platform/
   ├── backend/
   ├── frontend/
   ├── tests/
   └── README.md
   ```

---

### Bước 2: Khởi Động MongoDB

#### Cách 1: Chạy MongoDB như Windows Service (Tự động)
MongoDB thường tự động chạy sau khi cài đặt.

Kiểm tra bằng Task Manager → Services → MongoDB Server

#### Cách 2: Chạy MongoDB Thủ Công
Mở Command Prompt với quyền Administrator:
```cmd
cd "C:\Program Files\MongoDB\Server\7.0\bin"
mongod --dbpath "C:\data\db"
```

**Lưu ý:** Tạo thư mục `C:\data\db` trước nếu chưa có:
```cmd
mkdir C:\data\db
```

Kiểm tra MongoDB đang chạy:
```cmd
mongosh
```
Nếu kết nối thành công, gõ `exit` để thoát.

---

### Bước 3: Cấu Hình Backend

#### 3.1. Mở Command Prompt hoặc PowerShell

```cmd
cd C:\Projects\tradex-platform\backend
```

#### 3.2. Tạo Python Virtual Environment (Khuyến nghị)

```cmd
python -m venv venv
```

Kích hoạt virtual environment:

**Command Prompt:**
```cmd
venv\Scripts\activate
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Lưu ý PowerShell:** Nếu gặp lỗi execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3.3. Cài Đặt Dependencies

```cmd
pip install -r requirements.txt
```

#### 3.4. Cấu Hình File .env

Kiểm tra file `backend\.env`:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=http://localhost:3000
```

#### 3.5. Chạy Backend

```cmd
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Output mong đợi:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✅ Database initialized successfully
INFO:     Application startup complete.
```

Backend đang chạy tại: **http://localhost:8001**

---

### Bước 4: Cấu Hình Frontend

#### 4.1. Mở Terminal Mới (Giữ Backend Terminal Chạy)

Mở Command Prompt hoặc PowerShell thứ 2:

```cmd
cd C:\Projects\tradex-platform\frontend
```

#### 4.2. Cài Đặt Dependencies

```cmd
yarn install
```

Hoặc nếu gặp lỗi, dùng npm:
```cmd
npm install
```

#### 4.3. Cấu Hình File .env

Kiểm tra file `frontend\.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Quan trọng:** Backend URL phải trỏ đến localhost:8001

#### 4.4. Chạy Frontend

```cmd
yarn start
```

Hoặc:
```cmd
npm start
```

**Output mong đợi:**
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

Frontend sẽ tự động mở trình duyệt tại: **http://localhost:3000**

---

## 🎯 Truy Cập Ứng Dụng

### URLs
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs (Swagger UI)
- **MongoDB:** mongodb://localhost:27017

### Đăng Nhập Admin
- **Email:** admin@trading.com
- **Password:** Admin@123456

---

## 🛠️ Các Lệnh Hữu Ích

### Backend Commands

#### Chạy Backend
```cmd
cd backend
venv\Scripts\activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Kiểm Tra Backend Health
```cmd
curl http://localhost:8001/api/
```
Response: `{"message":"Hello World"}`

#### Xem MongoDB Data
```cmd
mongosh test_database
```
Trong MongoDB shell:
```javascript
show collections
db.admin_users.find({})
db.system_settings.find({})
```

### Frontend Commands

#### Chạy Frontend Development
```cmd
cd frontend
yarn start
```

#### Build Frontend Production
```cmd
yarn build
```

#### Test Frontend
```cmd
yarn test
```

---

## 🐛 Xử Lý Lỗi Thường Gặp

### Lỗi 1: MongoDB Connection Failed
```
pymongo.errors.ServerSelectionTimeoutError
```

**Giải pháp:**
1. Kiểm tra MongoDB đang chạy:
   ```cmd
   mongosh
   ```
2. Kiểm tra port 27017 có đang được sử dụng:
   ```cmd
   netstat -ano | findstr :27017
   ```
3. Restart MongoDB service:
   - Mở Services (services.msc)
   - Tìm "MongoDB Server"
   - Right-click → Restart

### Lỗi 2: Port 8001 đã được sử dụng
```
ERROR: [Errno 10048] Only one usage of each socket address
```

**Giải pháp:**
1. Tìm process đang dùng port:
   ```cmd
   netstat -ano | findstr :8001
   ```
2. Kill process (thay PID bằng số thực tế):
   ```cmd
   taskkill /PID <PID> /F
   ```
3. Hoặc đổi port trong backend:
   ```cmd
   python -m uvicorn server:app --port 8002 --reload
   ```

### Lỗi 3: Frontend không kết nối được Backend
```
Network Error / CORS Error
```

**Giải pháp:**
1. Kiểm tra Backend đang chạy tại http://localhost:8001
2. Kiểm tra file `frontend\.env`:
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```
3. Restart Frontend sau khi đổi .env
4. Xóa cache:
   ```cmd
   rd /s /q node_modules\.cache
   yarn start
   ```

### Lỗi 4: Module Not Found
```
ModuleNotFoundError: No module named 'xxx'
```

**Giải pháp:**
```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Lỗi 5: Python không được nhận diện
```
'python' is not recognized as an internal or external command
```

**Giải pháp:**
1. Thử dùng `python3` hoặc `py`:
   ```cmd
   py -m uvicorn server:app --reload
   ```
2. Hoặc thêm Python vào PATH:
   - Settings → System → Advanced System Settings
   - Environment Variables
   - Edit PATH → Add Python installation folder

### Lỗi 6: PowerShell Execution Policy
```
cannot be loaded because running scripts is disabled
```

**Giải pháp:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Lỗi 7: Yarn/NPM install failed
```
Error: EACCES: permission denied
```

**Giải pháp:**
```cmd
# Xóa node_modules và yarn.lock
rd /s /q node_modules
del yarn.lock
# Hoặc
del package-lock.json

# Cài lại
yarn install
# Hoặc
npm install
```

---

## 📝 Script Tự Động (Optional)

### Tạo file `start-backend.bat`
```batch
@echo off
cd backend
call venv\Scripts\activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
pause
```

### Tạo file `start-frontend.bat`
```batch
@echo off
cd frontend
yarn start
pause
```

### Tạo file `start-all.bat`
```batch
@echo off
echo Starting Trading Platform...
echo.

echo [1/2] Starting Backend...
start cmd /k "cd backend && call venv\Scripts\activate && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak

echo [2/2] Starting Frontend...
start cmd /k "cd frontend && yarn start"

echo.
echo ✅ All services started!
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo.
pause
```

**Cách dùng:** Double-click file `.bat` để chạy

---

## 🔧 Cấu Hình Nâng Cao

### Chạy Backend như Windows Service

#### Sử dụng NSSM (Non-Sucking Service Manager)

1. Tải NSSM: https://nssm.cc/download
2. Giải nén và mở Command Prompt (Administrator):
   ```cmd
   nssm install TradexBackend
   ```
3. Trong GUI:
   - Path: `C:\Projects\tradex-platform\backend\venv\Scripts\python.exe`
   - Startup directory: `C:\Projects\tradex-platform\backend`
   - Arguments: `-m uvicorn server:app --host 0.0.0.0 --port 8001`
4. Khởi động service:
   ```cmd
   nssm start TradexBackend
   ```

---

## 📊 Kiểm Tra Hệ Thống

### Test Backend API
```cmd
curl http://localhost:8001/api/
curl http://localhost:8001/docs
```

### Test Frontend
Mở browser: http://localhost:3000

### Test Database
```cmd
mongosh test_database --eval "db.admin_users.find()"
```

### Test Telegram Bot (Cần token)
```cmd
curl -X POST http://localhost:8001/api/admin/settings/test-telegram ^
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Workflow Hàng Ngày

### Bắt Đầu Làm Việc

1. **Khởi động MongoDB** (nếu chưa chạy)
   - Mở Services → Start MongoDB Server

2. **Khởi động Backend**
   ```cmd
   cd backend
   venv\Scripts\activate
   python -m uvicorn server:app --reload
   ```

3. **Khởi động Frontend** (Terminal mới)
   ```cmd
   cd frontend
   yarn start
   ```

### Kết Thúc Làm Việc

1. Stop Frontend: `Ctrl + C` trong terminal frontend
2. Stop Backend: `Ctrl + C` trong terminal backend
3. MongoDB có thể để chạy hoặc stop trong Services

---

## 📦 Production Build

### Build Frontend
```cmd
cd frontend
yarn build
```
Output: `frontend\build\` folder

### Build Backend (không cần build, nhưng có thể tạo executable)
```cmd
pip install pyinstaller
pyinstaller --onefile server.py
```

---

## 🔍 Logs và Debugging

### Backend Logs
Backend sẽ hiển thị logs trực tiếp trong terminal.

### Frontend Logs
1. Browser Console (F12)
2. Terminal logs khi chạy `yarn start`

### MongoDB Logs
```
C:\Program Files\MongoDB\Server\7.0\log\mongod.log
```

---

## 🎉 Hoàn Tất!

Sau khi làm theo hướng dẫn, bạn sẽ có:

✅ MongoDB đang chạy trên port 27017
✅ Backend đang chạy trên http://localhost:8001
✅ Frontend đang chạy trên http://localhost:3000
✅ Có thể đăng nhập Admin Panel
✅ KYC system hoạt động với Telegram Bot

### Các URL Quan Trọng
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001/api
- **Swagger Docs:** http://localhost:8001/docs
- **Admin Login:** http://localhost:3000/admin/login

### Tài Khoản Admin
- Email: `admin@trading.com`
- Password: `Admin@123456`

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra tất cả services đang chạy (MongoDB, Backend, Frontend)
2. Xem logs trong terminal
3. Kiểm tra file .env có đúng cấu hình
4. Xem phần "Xử Lý Lỗi Thường Gặp" ở trên

**Chúc bạn code vui vẻ!** 🚀
