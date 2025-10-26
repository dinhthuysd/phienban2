# 🔐 Google OAuth Setup Guide

## Hướng Dẫn Cấu Hình Google OAuth

### Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Đăng nhập bằng tài khoản Google của bạn
3. Nhấn **"Select a project"** → **"NEW PROJECT"**
4. Đặt tên project (ví dụ: "Trading Platform")
5. Nhấn **"CREATE"**

### Bước 2: Bật Google+ API

1. Trong menu bên trái, chọn **"APIs & Services"** → **"Library"**
2. Tìm kiếm **"Google+ API"**
3. Nhấn vào **"Google+ API"**
4. Nhấn **"ENABLE"**

### Bước 3: Tạo OAuth 2.0 Credentials

1. Trong menu bên trái, chọn **"APIs & Services"** → **"Credentials"**
2. Nhấn **"CREATE CREDENTIALS"** → **"OAuth client ID"**

3. **Nếu chưa có OAuth consent screen**, bạn sẽ được yêu cầu tạo:
   - Chọn **"External"** (cho phép bất kỳ ai có tài khoản Google đăng nhập)
   - Nhấn **"CREATE"**
   - Điền thông tin:
     * **App name**: Trading Platform
     * **User support email**: email của bạn
     * **Developer contact information**: email của bạn
   - Nhấn **"SAVE AND CONTINUE"** qua các bước
   - Nhấn **"BACK TO DASHBOARD"**

4. Quay lại **"Credentials"**, nhấn **"CREATE CREDENTIALS"** → **"OAuth client ID"**

5. Chọn **Application type**: **"Web application"**

6. **Authorized JavaScript origins** - Thêm các URL:
   ```
   http://localhost:3000
   https://your-production-domain.com
   ```

7. **Authorized redirect URIs** - Thêm các URL:
   ```
   http://localhost:3000
   http://localhost:3000/auth/callback
   https://your-production-domain.com
   https://your-production-domain.com/auth/callback
   ```

8. Nhấn **"CREATE"**

### Bước 4: Lưu Credentials

Sau khi tạo thành công, bạn sẽ thấy:
- **Client ID**: `1234567890-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-xxxxxxxxxxxxxxxxxxxx`

**⚠️ LƯU Ý**: Giữ Client Secret an toàn, không share công khai!

### Bước 5: Cấu Hình Backend

Cập nhật file `/app/backend/.env`:

```env
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

**Ví dụ:**
```env
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxx
```

### Bước 6: Cấu Hình Frontend

Cập nhật file `/app/frontend/.env`:

```env
REACT_APP_GOOGLE_CLIENT_ID=your-client-id-here
```

**Ví dụ:**
```env
REACT_APP_GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnop.apps.googleusercontent.com
```

### Bước 7: Restart Services

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

---

## 🎯 Tính Năng Đã Được Tích Hợp

### 1. ✅ Verification Badge (Dấu tích xanh)
- Icon verification badge màu xanh lam xuất hiện cạnh tên user
- Tooltip "Verified" khi hover vào icon
- Admin có thể bật/tắt verification cho từng user

### 2. ✅ Quản Lý User trong Admin Panel
- **Xem danh sách users** với filter và search
- **Icons đẹp mắt** cho các action:
  - 👁️ View: Xem chi tiết user
  - ✅ Activate/Deactivate: Bật/tắt tài khoản
  - 🗑️ Delete: Xóa user
- **Toggle verification badge** bằng Switch
- **Chi tiết user**: wallet, transactions, staking, investments

### 3. ✅ Tạo User từ Admin
- Form tạo user mới với đầy đủ thông tin:
  - Email, Username, Password
  - Full Name
  - Verification Badge (có thể bật ngay khi tạo)
  - Active Status
- Validation đầy đủ

### 4. ✅ Google OAuth cho User
- User có thể đăng nhập bằng Google
- Tự động tạo tài khoản nếu chưa có
- Link Google account với tài khoản existing

---

## 📋 Cách Sử Dụng

### Admin Panel - Quản Lý Users

1. Đăng nhập Admin Panel: `/admin/login`
2. Vào **Users** trong menu sidebar
3. Bạn sẽ thấy:
   - Danh sách tất cả users
   - Dấu tích xanh ✓ bên cạnh tên user đã verified
   - Switch để toggle verification
   - Icons để View, Activate/Deactivate, Delete

### Tạo User Mới

1. Nhấn nút **"Create User"**
2. Điền thông tin:
   - Email, Username, Password (bắt buộc)
   - Full Name (tùy chọn)
   - Bật **"Verified Badge"** nếu muốn user có dấu tích ngay
   - Bật **"Active Status"** để user có thể login
3. Nhấn **"Create User"**

### Toggle Verification Badge

1. Trong danh sách users, tìm user cần verify
2. Bật/tắt **Switch** trong cột "Verified"
3. Dấu tích xanh sẽ xuất hiện/biến mất ngay lập tức

---

## 🔧 API Endpoints Mới

### Backend APIs

#### 1. Toggle User Verification
```http
PUT /api/admin/users/{user_id}/verification?is_verified=true
Authorization: Bearer {admin_token}
```

#### 2. Create User (Admin)
```http
POST /api/admin/users/create
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "StrongPass123",
  "full_name": "John Doe",
  "is_verified": false,
  "is_active": true
}
```

#### 3. Delete User
```http
DELETE /api/admin/users/{user_id}
Authorization: Bearer {admin_token}
```

#### 4. Google OAuth Login
```http
POST /api/user/auth/google
Content-Type: application/json

{
  "token": "google-id-token"
}
```

---

## 🎨 UI Components

### Verification Badge Icon
```html
<i class="fi fi-ss-badge-check"></i>
```

Được load từ Flaticon CDN:
```html
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/2.0.0/uicons-solid-straight/css/uicons-solid-straight.css'>
```

---

## ⚠️ Lưu Ý Quan Trọng

1. **Google OAuth chỉ dành cho User**, không phải Admin
2. **Admin vẫn login bằng email/password** như cũ
3. **Verification badge không liên quan đến KYC** - đây là 2 tính năng riêng biệt
4. **Cần restart backend sau khi cập nhật .env file**

---

## 🐛 Troubleshooting

### Lỗi: "Google OAuth not configured"
- Kiểm tra `GOOGLE_CLIENT_ID` trong `/app/backend/.env`
- Restart backend: `sudo supervisorctl restart backend`

### Icon verification badge không hiển thị
- Kiểm tra Flaticon CSS đã được load trong `public/index.html`
- Clear browser cache

### User không thể login bằng Google
- Kiểm tra Authorized redirect URIs trong Google Console
- Đảm bảo domain của bạn đã được thêm vào whitelist

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. Backend logs: `tail -f /var/log/supervisor/backend.err.log`
2. Frontend console trong browser (F12 → Console)
3. Network tab để xem API calls

Chúc bạn thành công! 🎉
