import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Button } from '../ui/button';
import {
  LayoutDashboard,
  Users,
  FileText,
  Wallet,
  ArrowDownCircle,
  ArrowUpCircle,
  Receipt,
  FileCheck,
  Shield,
  LogOut,
  Menu,
  X,
  ChevronRight,
  Key,
  Lock,
  UserCog,
  Settings
} from 'lucide-react';

const AdminLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { admin, logout } = useAdminAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = [
    { path: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/admin/users', icon: Users, label: 'Users' },
    { path: '/admin/kyc', icon: Shield, label: 'KYC Verification' },
    { path: '/admin/documents', icon: FileText, label: 'Documents' },
    { path: '/admin/deposits', icon: ArrowDownCircle, label: 'Deposits' },
    { path: '/admin/withdrawals', icon: ArrowUpCircle, label: 'Withdrawals' },
    { path: '/admin/transactions', icon: Receipt, label: 'Transactions' },
    { path: '/admin/logs', icon: FileCheck, label: 'Audit Logs' },
    { path: '/admin/api-tokens', icon: Key, label: 'API Tokens', divider: true },
    { path: '/admin/api-permissions', icon: Lock, label: 'API Permissions' },
    { path: '/admin/admin-users', icon: UserCog, label: 'Admin Users', superAdminOnly: true },
    { path: '/admin/settings', icon: Settings, label: 'Settings', superAdminOnly: true },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/admin/login');
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-40 h-screen transition-transform ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } bg-slate-900 border-r border-slate-800 w-64`}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="flex items-center justify-between p-4 border-b border-slate-800">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-white font-bold text-lg">Admin Panel</h1>
                <p className="text-slate-400 text-xs">Trading Platform</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-1">
            {menuItems.map((item) => {
              // Hide super admin only items for non-super admins
              if (item.superAdminOnly && admin?.role !== 'super_admin') {
                return null;
              }
              
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <React.Fragment key={item.path}>
                  {item.divider && <div className="h-px bg-slate-800 my-3" />}
                  <Link
                    to={item.path}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                    {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
                  </Link>
                </React.Fragment>
              );
            })}
          </nav>

          {/* User Info & Logout */}
          <div className="p-4 border-t border-slate-800">
            <div className="bg-slate-800 rounded-lg p-3 mb-3">
              <p className="text-white font-medium text-sm">{admin?.full_name || 'Admin'}</p>
              <p className="text-slate-400 text-xs">{admin?.email}</p>
              <span className={`inline-block mt-2 px-2 py-1 rounded text-xs font-medium ${
                admin?.role === 'super_admin'
                  ? 'bg-purple-500/20 text-purple-300'
                  : admin?.role === 'admin'
                  ? 'bg-blue-500/20 text-blue-300'
                  : 'bg-green-500/20 text-green-300'
              }`}>
                {admin?.role?.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <Button
              onClick={handleLogout}
              variant="outline"
              className="w-full bg-slate-800 hover:bg-red-600 text-white border-slate-700"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`transition-all duration-300 ${
        sidebarOpen ? 'ml-64' : 'ml-0'
      }`}>
        {/* Top Bar */}
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-30">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
          >
            {sidebarOpen ? (
              <X className="w-6 h-6 text-slate-600" />
            ) : (
              <Menu className="w-6 h-6 text-slate-600" />
            )}
          </button>
          
          <div className="text-sm text-slate-600">
            {new Date().toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;