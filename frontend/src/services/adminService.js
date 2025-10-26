import api from './api';

class AdminService {
  // ============ AUTHENTICATION ============
  
  async login(email, password, totpCode = null) {
    const response = await api.post('/admin/auth/login', {
      email,
      password,
      totp_code: totpCode,
    });
    
    if (response.data.access_token) {
      localStorage.setItem('admin_token', response.data.access_token);
    }
    
    return response.data;
  }
  
  async getProfile() {
    const response = await api.get('/admin/auth/profile');
    localStorage.setItem('admin_user', JSON.stringify(response.data));
    return response.data;
  }
  
  async updateProfile(data) {
    const response = await api.put('/admin/auth/profile', data);
    return response.data;
  }
  
  async changePassword(oldPassword, newPassword) {
    const response = await api.post('/admin/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  }
  
  async logout() {
    try {
      await api.post('/admin/auth/logout');
    } finally {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_user');
    }
  }
  
  // ============ DASHBOARD ============
  
  async getDashboardStats() {
    const response = await api.get('/admin/dashboard');
    return response.data;
  }
  
  // ============ USER MANAGEMENT ============
  
  async getUsers(params = {}) {
    const response = await api.get('/admin/users', { params });
    return response.data;
  }
  
  async getUserDetail(userId) {
    const response = await api.get(`/admin/users/${userId}`);
    return response.data;
  }
  
  async updateUserStatus(userId, isActive) {
    const response = await api.put(`/admin/users/${userId}/status`, null, {
      params: { is_active: isActive },
    });
    return response.data;
  }

  async toggleUserVerification(userId, isVerified) {
    const response = await api.put(`/admin/users/${userId}/verification`, null, {
      params: { is_verified: isVerified },
    });
    return response.data;
  }

  async createUser(userData) {
    const response = await api.post('/admin/users/create', userData);
    return response.data;
  }

  async deleteUser(userId) {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  }
  
  // ============ KYC MANAGEMENT ============
  
  async getPendingKYC(params = {}) {
    const response = await api.get('/admin/kyc/pending', { params });
    return response.data;
  }
  
  async verifyKYC(kycId, approved, adminNote = null) {
    const response = await api.put(`/admin/kyc/${kycId}/verify`, null, {
      params: { approved, admin_note: adminNote },
    });
    return response.data;
  }
  
  // ============ DOCUMENT MANAGEMENT ============
  
  async getDocuments(params = {}) {
    const response = await api.get('/admin/documents', { params });
    return response.data;
  }
  
  async approveDocument(docId, approved, adminNote = null) {
    const response = await api.put(`/admin/documents/${docId}/approve`, null, {
      params: { approved, admin_note: adminNote },
    });
    return response.data;
  }
  
  // ============ DEPOSIT MANAGEMENT ============
  
  async getDeposits(params = {}) {
    const response = await api.get('/admin/deposits', { params });
    return response.data;
  }
  
  async processDeposit(depositId, approved, adminNote = null) {
    const response = await api.put(`/admin/deposits/${depositId}/process`, null, {
      params: { approved, admin_note: adminNote },
    });
    return response.data;
  }
  
  // ============ WITHDRAWAL MANAGEMENT ============
  
  async getWithdrawals(params = {}) {
    const response = await api.get('/admin/withdrawals', { params });
    return response.data;
  }
  
  async processWithdrawal(withdrawalId, approved, adminNote = null) {
    const response = await api.put(`/admin/withdrawals/${withdrawalId}/process`, null, {
      params: { approved, admin_note: adminNote },
    });
    return response.data;
  }
  
  // ============ TRANSACTIONS ============
  
  async getTransactions(params = {}) {
    const response = await api.get('/admin/transactions', { params });
    return response.data;
  }
  
  // ============ AUDIT LOGS ============
  
  async getAuditLogs(params = {}) {
    const response = await api.get('/admin/audit-logs', { params });
    return response.data;
  }
  
  // ============ API TOKEN MANAGEMENT ============
  
  async createAPIToken(tokenData) {
    const response = await api.post('/admin/api-tokens', tokenData);
    return response.data;
  }
  
  async getAPITokens(params = {}) {
    const response = await api.get('/admin/api-tokens', { params });
    return response.data;
  }
  
  async getAPITokenDetail(tokenId) {
    const response = await api.get(`/admin/api-tokens/${tokenId}`);
    return response.data;
  }
  
  async updateAPIToken(tokenId, updateData) {
    const response = await api.put(`/admin/api-tokens/${tokenId}`, updateData);
    return response.data;
  }
  
  async deleteAPIToken(tokenId) {
    const response = await api.delete(`/admin/api-tokens/${tokenId}`);
    return response.data;
  }
  
  // ============ API PERMISSIONS MANAGEMENT ============
  
  async createAPIPermission(permissionData) {
    const response = await api.post('/admin/api-permissions', permissionData);
    return response.data;
  }
  
  async getAPIPermissions(params = {}) {
    const response = await api.get('/admin/api-permissions', { params });
    return response.data;
  }
  
  async updateAPIPermission(permissionId, updateData) {
    const response = await api.put(`/admin/api-permissions/${permissionId}`, updateData);
    return response.data;
  }
  
  async deleteAPIPermission(permissionId) {
    const response = await api.delete(`/admin/api-permissions/${permissionId}`);
    return response.data;
  }
  
  // ============ ADMIN USERS MANAGEMENT ============
  
  async getAdminUsers(params = {}) {
    const response = await api.get('/admin/admin-users', { params });
    return response.data;
  }
  
  async getAdminUserDetail(adminId) {
    const response = await api.get(`/admin/admin-users/${adminId}`);
    return response.data;
  }
  
  async createAdminUser(adminData) {
    const response = await api.post('/admin/auth/register', adminData);
    return response.data;
  }
  
  async updateAdminUserStatus(adminId, isActive) {
    const response = await api.put(`/admin/admin-users/${adminId}/status`, null, {
      params: { is_active: isActive },
    });
    return response.data;
  }
  
  async updateAdminUserRole(adminId, newRole) {
    const response = await api.put(`/admin/admin-users/${adminId}/role`, null, {
      params: { new_role: newRole },
    });
    return response.data;
  }
  
  async deleteAdminUser(adminId) {
    const response = await api.delete(`/admin/admin-users/${adminId}`);
    return response.data;
  }
  
  // ============ SYSTEM SETTINGS ============
  
  async getSettings() {
    const response = await api.get('/admin/settings');
    return response.data;
  }
  
  async updateSettings(settingsData) {
    const response = await api.put('/admin/settings', settingsData);
    return response.data;
  }
  
  async resetSettings() {
    const response = await api.post('/admin/settings/reset');
    return response.data;
  }
}

export default new AdminService();