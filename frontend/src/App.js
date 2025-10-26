import React, { useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { AdminAuthProvider } from "./contexts/AdminAuthContext";
import { Toaster } from "./components/ui/toaster";

// Admin imports
import { 
  AdminLogin, 
  AdminDashboard, 
  AdminUsers, 
  AdminDeposits, 
  AdminWithdrawals,
  AdminKYC,
  AdminDocuments,
  AdminTransactions,
  AdminLogs,
  AdminAPITokens,
  AdminAPIPermissions,
  AdminUsersManagement,
  AdminSettings
} from "./pages/admin";
import AdminLayout from "./components/admin/AdminLayout";
import ProtectedAdminRoute from "./components/admin/ProtectedAdminRoute";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div>
      <header className="App-header">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-white mb-4">Trading Platform</h1>
          <p className="text-xl text-slate-300">Admin Panel System Ready</p>
          <div className="mt-8">
            <a
              href="/admin/login"
              className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all"
            >
              Go to Admin Panel
            </a>
          </div>
        </div>
      </header>
    </div>
  );
};

function App() {
  return (
    <AdminAuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Home />} />
            
            {/* Admin Routes */}
            <Route path="/admin/login" element={<AdminLogin />} />
            
            <Route path="/admin" element={
              <ProtectedAdminRoute>
                <AdminLayout />
              </ProtectedAdminRoute>
            }>
              <Route index element={<Navigate to="/admin/dashboard" replace />} />
              <Route path="dashboard" element={<AdminDashboard />} />
              <Route path="users" element={<AdminUsers />} />
              <Route path="kyc" element={<AdminKYC />} />
              <Route path="documents" element={<AdminDocuments />} />
              <Route path="deposits" element={<AdminDeposits />} />
              <Route path="withdrawals" element={<AdminWithdrawals />} />
              <Route path="transactions" element={<AdminTransactions />} />
              <Route path="logs" element={<AdminLogs />} />
              <Route path="api-tokens" element={<AdminAPITokens />} />
              <Route path="api-permissions" element={<AdminAPIPermissions />} />
              <Route path="admin-users" element={<AdminUsersManagement />} />
              <Route path="settings" element={<AdminSettings />} />
            </Route>
            
            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </div>
    </AdminAuthProvider>
  );
}

export default App;
