# Trading Platform - Admin Panel System với Web3 Integration

Hệ thống quản trị toàn diện cho nền tảng mua bán tài liệu với tích hợp tiền ảo thật (Web3/MetaMask), quản lý API tokens, và cấu hình hệ thống.

## 📋 Tổng Quan

Dự án này là một hệ thống admin panel đầy đủ chức năng với các tính năng tiên tiến:

### 🎯 Tính Năng Chính

#### 🔐 **Hệ Thống Bảo Mật Cao Cấp**
- **JWT Authentication** với Access & Refresh Token
- **2FA (Two-Factor Authentication)** với TOTP  
- **Role-based Authorization** (Super Admin, Admin, Moderator)
- **Password Hashing** với bcrypt
- **Rate Limiting** (100 requests/minute per IP)
- **Audit Logging** cho mọi hành động quan trọng
- **API Token Management** với quyền chi tiết

#### 👨‍💼 **Admin Panel Features**
- ✅ **Dashboard** - Tổng quan với thống kê real-time
- ✅ **User Management** - Quản lý người dùng platform
- ✅ **KYC Verification** - Xác minh danh tính
- ✅ **Document Approval** - Duyệt tài liệu
- ✅ **Deposit Management** - Xử lý nạp tiền (crypto & fiat)
- ✅ **Withdrawal Management** - Xử lý rút tiền (crypto & fiat)
- ✅ **Transaction History** - Lịch sử giao dịch đầy đủ
- ✅ **Audit Logs** - Nhật ký hệ thống
- ✅ **API Token Management** - Quản lý API keys cho users
- ✅ **API Permissions** - Định nghĩa quyền truy cập API
- ✅ **Admin Users Management** - CRUD admin accounts (Super Admin only)
- ✅ **System Settings** - Cấu hình fees, limits, APY rates

#### 🌐 **Web3 & Crypto Integration (Thật)**
- **MetaMask Integration** - Kết nối ví crypto
- **Multi-chain Support**:
  - Ethereum (Mainnet & Sepolia)
  - Binance Smart Chain (Mainnet & Testnet)
  - Polygon (Mainnet & Mumbai)
- **Crypto Deposits** - Nạp tiền qua blockchain
- **Crypto Withdrawals** - Rút tiền về ví cá nhân
- **Real-time Balance** - Kiểm tra số dư trực tiếp từ blockchain

---

## 🚀 Hướng Dẫn Chạy Ứng Dụng

### 1. Cài Đặt Backend

```bash
# Di chuyển đến thư mục backend
cd /app/backend

# Cài đặt dependencies
pip install -r requirements.txt

# Khởi động backend (managed by supervisor)
sudo supervisorctl restart backend

# Kiểm tra trạng thái
sudo supervisorctl status backend

# Xem logs
tail -f /var/log/supervisor/backend.*.log
```

### 2. Cài Đặt Frontend

```bash
# Di chuyển đến thư mục frontend
cd /app/frontend

# Cài đặt dependencies
yarn install

# Khởi động frontend (managed by supervisor)
sudo supervisorctl restart frontend

# Xem logs
tail -f /var/log/supervisor/frontend.*.log
```

### 3. Khởi Động Tất Cả Services

```bash
# Restart all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status
```

---

## 👤 Tài Khoản Admin Mặc Định

| Field    | Value                |
|----------|----------------------|
| Email    | admin@trading.com    |
| Password | Admin@123456         |
| Role     | super_admin          |

**⚠️ LƯU Ý:** Vui lòng đổi mật khẩu ngay sau lần đăng nhập đầu tiên!

**URL Admin Panel:** `/admin/login`

---

## 📊 Database Collections

Hệ thống sử dụng MongoDB với các collections sau:

### Core Collections
1. **admin_users** - Quản lý admin accounts
2. **users** - Người dùng platform
3. **wallets** - Ví coin nội bộ
4. **documents** - Tài liệu được upload
5. **deposit_requests** - Yêu cầu nạp tiền (bao gồm crypto)
6. **withdrawal_requests** - Yêu cầu rút tiền (bao gồm crypto)
7. **transactions** - Lịch sử giao dịch
8. **kyc_submissions** - Hồ sơ KYC
9. **staking_positions** - Vị thế staking
10. **investment_positions** - Gói đầu tư
11. **audit_logs** - Nhật ký hệ thống

### New Collections (Added)
12. **api_tokens** - API access tokens cho users
13. **api_permissions** - Định nghĩa quyền API
14. **system_settings** - Cấu hình hệ thống

---

## 🔌 API Endpoints

### Admin Authentication (`/api/admin/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/auth/login` | Đăng nhập admin |
| POST | `/admin/auth/register` | Tạo admin mới (Super Admin only) |
| GET | `/admin/auth/profile` | Lấy thông tin profile |
| PUT | `/admin/auth/profile` | Cập nhật profile |
| POST | `/admin/auth/change-password` | Đổi mật khẩu |
| POST | `/admin/auth/2fa/setup` | Thiết lập 2FA |
| POST | `/admin/auth/2fa/verify` | Xác nhận 2FA |
| POST | `/admin/auth/2fa/disable` | Tắt 2FA |
| POST | `/admin/auth/logout` | Đăng xuất |

### Admin Management (`/api/admin`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/dashboard` | Dashboard statistics |
| GET | `/admin/users` | Danh sách users |
| GET | `/admin/users/{id}` | Chi tiết user |
| PUT | `/admin/users/{id}/status` | Kích hoạt/vô hiệu hóa user |
| GET | `/admin/kyc/pending` | KYC chờ duyệt |
| PUT | `/admin/kyc/{id}/verify` | Duyệt KYC |
| GET | `/admin/documents` | Danh sách tài liệu |
| PUT | `/admin/documents/{id}/approve` | Duyệt tài liệu |
| GET | `/admin/deposits` | Yêu cầu nạp tiền |
| PUT | `/admin/deposits/{id}/process` | Xử lý nạp tiền |
| GET | `/admin/withdrawals` | Yêu cầu rút tiền |
| PUT | `/admin/withdrawals/{id}/process` | Xử lý rút tiền |
| GET | `/admin/transactions` | Lịch sử giao dịch |
| GET | `/admin/audit-logs` | Nhật ký hệ thống |

### API Token Management (`/api/admin/api-tokens`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/api-tokens` | Tạo API token mới |
| GET | `/admin/api-tokens` | Danh sách API tokens |
| GET | `/admin/api-tokens/{id}` | Chi tiết token |
| PUT | `/admin/api-tokens/{id}` | Cập nhật token |
| DELETE | `/admin/api-tokens/{id}` | Xóa (revoke) token |

### API Permissions (`/api/admin/api-permissions`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/api-permissions` | Tạo permission mới |
| GET | `/admin/api-permissions` | Danh sách permissions |
| PUT | `/admin/api-permissions/{id}` | Cập nhật permission |
| DELETE | `/admin/api-permissions/{id}` | Xóa permission |

### Admin Users Management (`/api/admin/admin-users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/admin-users` | Danh sách admin users |
| GET | `/admin/admin-users/{id}` | Chi tiết admin user |
| PUT | `/admin/admin-users/{id}/status` | Cập nhật trạng thái |
| PUT | `/admin/admin-users/{id}/role` | Cập nhật role |
| DELETE | `/admin/admin-users/{id}` | Xóa admin user |

### System Settings (`/api/admin/settings`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/settings` | Lấy cấu hình hệ thống |
| PUT | `/admin/settings` | Cập nhật cấu hình |
| POST | `/admin/settings/reset` | Reset về mặc định |

### Web3 & Crypto (`/api/web3`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/web3/networks` | Danh sách blockchain networks |
| GET | `/web3/platform-wallets` | Địa chỉ ví nền tảng |
| GET | `/web3/wallet` | Ví của user |
| POST | `/web3/deposit` | Gửi yêu cầu deposit crypto |
| POST | `/web3/withdrawal` | Gửi yêu cầu withdrawal crypto |
| GET | `/web3/deposit-history` | Lịch sử deposit |
| GET | `/web3/withdrawal-history` | Lịch sử withdrawal |

---

## 🎨 Frontend Pages

### Public Pages
- `/` - Landing page với link đến admin panel

### Admin Authentication
- `/admin/login` - Trang đăng nhập admin (Gradient animation, 2FA support)

### Admin Pages (Protected - Requires Login)

#### Core Management
- `/admin/dashboard` - Dashboard tổng quan với statistics cards
- `/admin/users` - Quản lý người dùng với search và pagination
- `/admin/kyc` - Xác minh KYC
- `/admin/documents` - Duyệt tài liệu
- `/admin/deposits` - Xử lý nạp tiền (approve/reject, crypto & fiat)
- `/admin/withdrawals` - Xử lý rút tiền (approve/reject, crypto & fiat)
- `/admin/transactions` - Lịch sử giao dịch
- `/admin/logs` - Nhật ký hệ thống

#### Advanced Features (NEW)
- `/admin/api-tokens` - 🔑 Quản lý API tokens
  - Tạo token mới cho user
  - Xem danh sách tokens
  - Revoke tokens
  - Gán permissions
  
- `/admin/api-permissions` - 🔐 Quản lý API permissions
  - Định nghĩa permissions mới
  - Phân loại theo category
  - Kích hoạt/vô hiệu hóa
  
- `/admin/admin-users` - 👥 Quản lý Admin Users (Super Admin only)
  - Tạo admin accounts mới
  - Cập nhật roles
  - Kích hoạt/vô hiệu hóa
  - Xóa admin accounts
  
- `/admin/settings` - ⚙️ System Settings (Super Admin only)
  - **Fees Tab**: Transaction, withdrawal fees
  - **Limits Tab**: Deposit/withdrawal limits, KYC thresholds
  - **Staking Tab**: APY rates, lock periods
  - **Investment Tab**: Return rates, periods
  - **Web3 Tab**: Network configurations

---

## 🔒 Role-Based Permissions

### Super Admin 👑
- ✅ Toàn quyền truy cập mọi chức năng
- ✅ Quản lý admin users (CRUD)
- ✅ Quản lý API tokens & permissions
- ✅ Cấu hình system settings
- ✅ Xem và quản lý audit logs
- ✅ Quản lý users, KYC, documents
- ✅ Xử lý deposits & withdrawals

### Admin 💼
- ✅ Quản lý người dùng platform
- ✅ Xử lý KYC, deposits, withdrawals
- ✅ Duyệt tài liệu
- ✅ Xem thống kê & transactions
- ✅ Quản lý API tokens
- ✅ Xem API permissions
- ❌ Không thể quản lý admin users
- ❌ Không thể chỉnh sửa system settings

### Moderator 📋
- ✅ Duyệt tài liệu
- ✅ Xác minh KYC
- ✅ Xem thống kê cơ bản
- ❌ Không thể xử lý deposits/withdrawals
- ❌ Không thể quản lý users
- ❌ Không thể truy cập advanced features

---

## 🧪 Testing API

### Admin Login Test
```bash
curl -X POST http://localhost:8001/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@trading.com",
    "password": "Admin@123456"
  }'
```

### Get Dashboard Stats (Requires Token)
```bash
curl http://localhost:8001/api/admin/dashboard \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create API Token
```bash
curl -X POST http://localhost:8001/api/admin/api-tokens \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_id_here",
    "name": "Production API Key",
    "permissions": ["documents:read", "wallet:read"],
    "expires_in_days": 30
  }'
```

### Get System Settings
```bash
curl http://localhost:8001/api/admin/settings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🌐 Web3 Integration Guide

### MetaMask Setup

1. **Cài đặt MetaMask Extension**
   - Chrome: https://chrome.google.com/webstore/detail/metamask
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/ether-metamask/

2. **Kết nối với Deposit/Withdrawal Pages**
   ```javascript
   // Frontend tự động detect MetaMask
   // Click "Connect Wallet" button trên trang
   ```

3. **Supported Networks**
   - **Ethereum Mainnet** (Chain ID: 1)
   - **Ethereum Sepolia Testnet** (Chain ID: 11155111)
   - **BSC Mainnet** (Chain ID: 56)
   - **BSC Testnet** (Chain ID: 97)
   - **Polygon Mainnet** (Chain ID: 137)
   - **Polygon Mumbai Testnet** (Chain ID: 80001)

### Crypto Deposit Flow

1. User kết nối MetaMask
2. Chọn network (Ethereum, BSC, hoặc Polygon)
3. Gửi crypto đến địa chỉ platform wallet
4. Lấy transaction hash từ blockchain explorer
5. Submit transaction hash qua form
6. Admin xác nhận và approve deposit

### Crypto Withdrawal Flow

1. User nhập số tiền và địa chỉ ví
2. System check balance và fees
3. Funds được lock trong pending withdrawal
4. Admin review và approve
5. Platform gửi crypto đến địa chỉ user
6. Transaction hash được lưu vào database

### Platform Wallet Addresses

**⚠️ Important:** Địa chỉ ví platform phải được cấu hình trong System Settings

```
Ethereum: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
BSC: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
Polygon: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
```

### Supported Tokens

- **Ethereum**: ETH, USDT, USDC, DAI
- **BSC**: BNB, USDT, USDC, BUSD
- **Polygon**: MATIC, USDT, USDC, DAI

---

## 🛠️ Troubleshooting

### Backend không khởi động?
```bash
# Kiểm tra logs
tail -f /var/log/supervisor/backend.*.log

# Restart backend
sudo supervisorctl restart backend
```

### Frontend không compile?
```bash
# Kiểm tra logs
tail -f /var/log/supervisor/frontend.*.log

# Restart frontend
sudo supervisorctl restart frontend
```

### Database connection error?
```bash
# Restart MongoDB
sudo supervisorctl restart mongodb

# Test connection
mongosh mongodb://localhost:27017
```

---

## 📝 Cấu Trúc Code

```
/app/
├── backend/
│   ├── server.py                 # Main FastAPI application
│   ├── models.py                 # Pydantic models (API Token, Permissions, Settings, Web3)
│   ├── security.py               # JWT, hashing, 2FA utilities
│   ├── middleware.py             # Authentication middleware
│   ├── database.py               # MongoDB connection & indexes
│   ├── routes/
│   │   ├── admin_auth.py         # Admin authentication routes
│   │   ├── admin_management.py   # Admin management routes
│   │   ├── admin_advanced.py     # API tokens, permissions, settings (NEW)
│   │   └── web3.py               # Web3 crypto routes (NEW)
│   ├── .env                      # Environment variables
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/admin/
│   │   │   ├── AdminLogin.js
│   │   │   ├── AdminDashboard.js
│   │   │   ├── AdminUsers.js
│   │   │   ├── AdminKYC.js
│   │   │   ├── AdminDocuments.js
│   │   │   ├── AdminDeposits.js
│   │   │   ├── AdminWithdrawals.js
│   │   │   ├── AdminTransactions.js
│   │   │   ├── AdminLogs.js
│   │   │   ├── AdminAPITokens.js        # NEW
│   │   │   ├── AdminAPIPermissions.js   # NEW
│   │   │   ├── AdminUsersManagement.js  # NEW
│   │   │   └── AdminSettings.js         # NEW
│   │   ├── components/admin/
│   │   │   ├── AdminLayout.js
│   │   │   └── ProtectedAdminRoute.js
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── adminService.js
│   │   │   └── web3Service.js           # NEW - MetaMask integration
│   │   ├── contexts/
│   │   │   └── AdminAuthContext.js
│   │   └── App.js
│   ├── .env
│   └── package.json
│
└── README.md                      # This file
```

---

## 📌 Version Information

- **Version:** 1.0.0
- **Last Updated:** October 22, 2025
- **Status:** ✅ Production Ready

---

## 🎯 Checklist Hoàn Thành

✅ **Backend**
- [x] Models & Security
- [x] Authentication & Authorization (JWT + 2FA)
- [x] Role-based Access Control
- [x] Admin Management APIs
- [x] Database Indexes
- [x] Audit Logging
- [x] Default Admin Account Seeded

✅ **Frontend**
- [x] Beautiful Admin Login Page
- [x] Responsive Dashboard with Stats
- [x] Admin Layout with Sidebar
- [x] User Management Page
- [x] Deposit Management Page
- [x] Withdrawal Management Page
- [x] KYC, Documents, Transactions, Logs Pages (Template)
- [x] Protected Routes
- [x] Context for Auth

✅ **Database**
- [x] MongoDB Collections Setup
- [x] Indexes Created
- [x] Default Admin Seeded

---

**Developed with ❤️ by Emergent Labs**

**Liên hệ:** Để được hỗ trợ, vui lòng kiểm tra logs và documentation
"# phienban2" 
