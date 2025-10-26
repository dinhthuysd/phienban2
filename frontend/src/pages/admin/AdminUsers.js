import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../../components/ui/tooltip';
import { Switch } from '../../components/ui/switch';
import { useToast } from '../../hooks/use-toast';
import adminService from '../../services/adminService';
import {
  Users,
  Plus,
  Trash2,
  Eye,
  CheckCircle,
  XCircle,
  Search,
  Filter,
  Mail,
  User,
  Key,
  UserCheck,
  UserX,
  Shield,
  ShieldCheck,
  ShieldOff,
  CreditCard,
  BarChart3,
  Activity,
  Calendar,
  Edit3,
  MoreVertical,
  Download,
  RefreshCw,
  AlertTriangle,
  Info,
  Crown,
  Star,
  TrendingUp,
  Lock,
  Unlock,
  Phone,
  IdCard,
  FileText,
  Clock,
  CheckSquare,
  XSquare,
  Settings,
  Wallet,
  DollarSign,
  PieChart
} from 'lucide-react';

const AdminUsers = () => {
  const { toast } = useToast();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 });
  const [search, setSearch] = useState('');
  const [kycFilter, setKycFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    phone: '',
    is_verified: false,
    is_active: true,
    is_premium: false
  });

  useEffect(() => {
    fetchUsers();
  }, [pagination.page, search, kycFilter, statusFilter]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        limit: pagination.limit,
      };
      
      if (search) params.search = search;
      if (kycFilter && kycFilter !== 'all') params.kyc_status = kycFilter;
      if (statusFilter && statusFilter !== 'all') params.is_active = statusFilter === 'active';
      
      const data = await adminService.getUsers(params);
      setUsers(data.users || []);
      setPagination(prev => ({ ...prev, total: data.total, pages: data.pages }));
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to fetch users',
        variant: 'destructive',
        icon: <AlertTriangle className="w-5 h-5" />
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      if (!formData.email || !formData.username || !formData.password) {
        toast({
          title: 'Validation Error',
          description: 'Please fill all required fields',
          variant: 'destructive',
          icon: <AlertTriangle className="w-5 h-5" />
        });
        return;
      }

      await adminService.createUser(formData);
      setShowCreateDialog(false);
      fetchUsers();
      
      // Reset form
      setFormData({
        email: '',
        username: '',
        password: '',
        full_name: '',
        phone: '',
        is_verified: false,
        is_active: true,
        is_premium: false
      });
      
      toast({
        title: 'Success',
        description: 'User created successfully',
        icon: <CheckCircle className="w-5 h-5" />
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create user',
        variant: 'destructive',
        icon: <XCircle className="w-5 h-5" />
      });
    }
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    try {
      setActionLoading(`status-${userId}`);
      await adminService.updateUserStatus(userId, !currentStatus);
      fetchUsers();
      toast({
        title: 'Success',
        description: `User ${!currentStatus ? 'activated' : 'deactivated'}`,
        icon: <CheckCircle className="w-5 h-5" />
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update user status',
        variant: 'destructive',
        icon: <XCircle className="w-5 h-5" />
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleVerification = async (userId, currentVerified) => {
    try {
      setActionLoading(`verify-${userId}`);
      await adminService.toggleUserVerification(userId, !currentVerified);
      fetchUsers();
      toast({
        title: 'Success',
        description: `User verification ${!currentVerified ? 'enabled' : 'disabled'}`,
        icon: <ShieldCheck className="w-5 h-5" />
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update verification status',
        variant: 'destructive',
        icon: <ShieldOff className="w-5 h-5" />
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleTogglePremium = async (userId, currentPremium) => {
    try {
      setActionLoading(`premium-${userId}`);
      await adminService.toggleUserPremium(userId, !currentPremium);
      fetchUsers();
      toast({
        title: 'Success',
        description: `Premium status ${!currentPremium ? 'granted' : 'revoked'}`,
        icon: <Crown className="w-5 h-5" />
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update premium status',
        variant: 'destructive',
        icon: <XCircle className="w-5 h-5" />
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }
    
    try {
      setActionLoading(`delete-${userId}`);
      await adminService.deleteUser(userId);
      fetchUsers();
      toast({
        title: 'Success',
        description: 'User deleted successfully',
        icon: <CheckCircle className="w-5 h-5" />
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete user',
        variant: 'destructive',
        icon: <XCircle className="w-5 h-5" />
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleViewDetail = async (userId) => {
    try {
      setActionLoading(`view-${userId}`);
      const data = await adminService.getUserDetail(userId);
      setSelectedUser(data);
      setShowDetailDialog(true);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch user details',
        variant: 'destructive',
        icon: <AlertTriangle className="w-5 h-5" />
      });
    } finally {
      setActionLoading(null);
    }
  };

  const getKycBadge = (status) => {
    const badges = {
      verified: (
        <Badge className="bg-green-500 flex items-center gap-1 w-fit">
          <ShieldCheck className="w-3 h-3" />
          Verified
        </Badge>
      ),
      pending: (
        <Badge className="bg-yellow-500 flex items-center gap-1 w-fit">
          <Clock className="w-3 h-3" />
          Pending
        </Badge>
      ),
      rejected: (
        <Badge className="bg-red-500 flex items-center gap-1 w-fit">
          <XCircle className="w-3 h-3" />
          Rejected
        </Badge>
      ),
    };
    return badges[status] || <Badge variant="secondary">Unknown</Badge>;
  };

  const getStatusBadge = (isActive) => {
    return isActive ? (
      <Badge className="bg-green-500 flex items-center gap-1 w-fit">
        <CheckCircle className="w-3 h-3" />
        Active
      </Badge>
    ) : (
      <Badge variant="destructive" className="flex items-center gap-1 w-fit">
        <XCircle className="w-3 h-3" />
        Inactive
      </Badge>
    );
  };

  const exportUsers = () => {
    toast({
      title: 'Export Started',
      description: 'Preparing user data for export...',
      icon: <Download className="w-5 h-5" />
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-8 h-8 text-blue-600" />
            Users Management
          </h1>
          <p className="text-slate-600 mt-1 flex items-center gap-1">
            <Settings className="w-4 h-4" />
            Manage platform users and verification status
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportUsers} className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </Button>
          <Button onClick={fetchUsers} variant="outline" className="flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
          <Button onClick={() => setShowCreateDialog(true)} className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Create User
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Total Users</p>
                <p className="text-2xl font-bold mt-1">{pagination.total}</p>
              </div>
              <Users className="w-8 h-8 text-blue-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Active Users</p>
                <p className="text-2xl font-bold mt-1">
                  {users.filter(u => u.is_active).length}
                </p>
              </div>
              <UserCheck className="w-8 h-8 text-green-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Verified KYC</p>
                <p className="text-2xl font-bold mt-1">
                  {users.filter(u => u.kyc_status === 'verified').length}
                </p>
              </div>
              <ShieldCheck className="w-8 h-8 text-purple-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-r from-amber-500 to-amber-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-amber-100 text-sm">Premium Users</p>
                <p className="text-2xl font-bold mt-1">
                  {users.filter(u => u.is_premium).length}
                </p>
              </div>
              <Crown className="w-8 h-8 text-amber-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="search" className="flex items-center gap-2 mb-2">
                <Search className="w-4 h-4" />
                Search
              </Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  id="search"
                  placeholder="Search by email, username, or name..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="kyc_filter" className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4" />
                KYC Status
              </Label>
              <Select value={kycFilter} onValueChange={setKycFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All statuses</SelectItem>
                  <SelectItem value="verified">Verified</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="status_filter" className="flex items-center gap-2 mb-2">
                <Activity className="w-4 h-4" />
                Status
              </Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All users" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All users</SelectItem>
                  <SelectItem value="active">Active only</SelectItem>
                  <SelectItem value="inactive">Inactive only</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-end">
              <Button onClick={fetchUsers} className="w-full bg-blue-600 hover:bg-blue-700 flex items-center gap-2">
                <Filter className="w-4 h-4" />
                Apply Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Platform Users
            <Badge variant="secondary" className="ml-2">
              {pagination.total}
            </Badge>
          </CardTitle>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Info className="w-4 h-4" />
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-slate-600 flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                Loading users...
              </p>
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <UserX className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p className="text-lg font-medium">No users found</p>
              <p className="text-sm mt-1">Try adjusting your search or filters</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User Information</TableHead>
                      <TableHead>Contact</TableHead>
                      <TableHead>KYC Status</TableHead>
                      <TableHead>Account Status</TableHead>
                      <TableHead>Verification</TableHead>
                      <TableHead>Premium</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((user) => (
                      <TableRow key={user.id} className="hover:bg-slate-50/50">
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                              {user.username?.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <p className="font-semibold text-slate-900">{user.username}</p>
                                {user.is_verified && (
                                  <TooltipProvider>
                                    <Tooltip>
                                      <TooltipTrigger>
                                        <Badge className="bg-blue-500 px-1">
                                          <CheckCircle className="w-3 h-3" />
                                        </Badge>
                                      </TooltipTrigger>
                                      <TooltipContent>
                                        <p>Verified User</p>
                                      </TooltipContent>
                                    </Tooltip>
                                  </TooltipProvider>
                                )}
                                {user.is_premium && (
                                  <TooltipProvider>
                                    <Tooltip>
                                      <TooltipTrigger>
                                        <Badge className="bg-amber-500 px-1">
                                          <Crown className="w-3 h-3" />
                                        </Badge>
                                      </TooltipTrigger>
                                      <TooltipContent>
                                        <p>Premium User</p>
                                      </TooltipContent>
                                    </Tooltip>
                                  </TooltipProvider>
                                )}
                              </div>
                              {user.full_name && (
                                <div className="text-sm text-slate-600 flex items-center gap-1">
                                  <User className="w-3 h-3" />
                                  {user.full_name}
                                </div>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2 text-sm">
                              <Mail className="w-3 h-3 text-slate-400" />
                              {user.email}
                            </div>
                            {user.phone && (
                              <div className="flex items-center gap-2 text-sm text-slate-600">
                                <Phone className="w-3 h-3 text-slate-400" />
                                {user.phone}
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>{getKycBadge(user.kyc_status)}</TableCell>
                        <TableCell>{getStatusBadge(user.is_active)}</TableCell>
                        <TableCell>
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div>
                                  <Switch
                                    checked={user.is_verified}
                                    onCheckedChange={() => handleToggleVerification(user.id, user.is_verified)}
                                    disabled={actionLoading === `verify-${user.id}`}
                                    className={user.is_verified ? 'data-[state=checked]:bg-green-500' : ''}
                                  />
                                </div>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>{user.is_verified ? 'Revoke verification' : 'Grant verification'}</p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        </TableCell>
                        <TableCell>
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div>
                                  <Switch
                                    checked={user.is_premium}
                                    onCheckedChange={() => handleTogglePremium(user.id, user.is_premium)}
                                    disabled={actionLoading === `premium-${user.id}`}
                                    className={user.is_premium ? 'data-[state=checked]:bg-amber-500' : ''}
                                  />
                                </div>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>{user.is_premium ? 'Revoke premium' : 'Grant premium'}</p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2 text-sm text-slate-600">
                            <Calendar className="w-3 h-3" />
                            {new Date(user.created_at).toLocaleDateString()}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center justify-end gap-1">
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleViewDetail(user.id)}
                                    disabled={actionLoading === `view-${user.id}`}
                                    className="h-8 w-8 p-0 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                  >
                                    {actionLoading === `view-${user.id}` ? (
                                      <RefreshCw className="w-3 h-3 animate-spin" />
                                    ) : (
                                      <Eye className="w-3 h-3" />
                                    )}
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>View Details</TooltipContent>
                              </Tooltip>
                            </TooltipProvider>

                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleToggleStatus(user.id, user.is_active)}
                                    disabled={actionLoading === `status-${user.id}`}
                                    className={`h-8 w-8 p-0 ${
                                      user.is_active 
                                        ? "text-orange-600 hover:text-orange-700 hover:bg-orange-50" 
                                        : "text-green-600 hover:text-green-700 hover:bg-green-50"
                                    }`}
                                  >
                                    {actionLoading === `status-${user.id}` ? (
                                      <RefreshCw className="w-3 h-3 animate-spin" />
                                    ) : user.is_active ? (
                                      <UserX className="w-3 h-3" />
                                    ) : (
                                      <UserCheck className="w-3 h-3" />
                                    )}
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                  {user.is_active ? 'Deactivate' : 'Activate'}
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>

                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleDeleteUser(user.id)}
                                    disabled={actionLoading === `delete-${user.id}`}
                                    className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                                  >
                                    {actionLoading === `delete-${user.id}` ? (
                                      <RefreshCw className="w-3 h-3 animate-spin" />
                                    ) : (
                                      <Trash2 className="w-3 h-3" />
                                    )}
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Delete User</TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-slate-600 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  Showing {users.length} of {pagination.total} users
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                    disabled={pagination.page === 1}
                    className="flex items-center gap-2"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    Previous
                  </Button>
                  <div className="flex items-center px-4 text-sm font-medium text-slate-700">
                    Page {pagination.page} of {pagination.pages || 1}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                    disabled={pagination.page >= (pagination.pages || 1)}
                    className="flex items-center gap-2"
                  >
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Create User Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Create New User
            </DialogTitle>
            <DialogDescription>
              Add a new user to the platform with password authentication
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="email" className="flex items-center gap-2 mb-2">
                <Mail className="w-4 h-4" />
                Email *
              </Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="user@example.com"
              />
            </div>
            
            <div>
              <Label htmlFor="username" className="flex items-center gap-2 mb-2">
                <User className="w-4 h-4" />
                Username *
              </Label>
              <Input
                id="username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="johndoe"
              />
            </div>
            
            <div>
              <Label htmlFor="full_name" className="flex items-center gap-2 mb-2">
                <IdCard className="w-4 h-4" />
                Full Name
              </Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="John Doe"
              />
            </div>

            <div>
              <Label htmlFor="phone" className="flex items-center gap-2 mb-2">
                <Phone className="w-4 h-4" />
                Phone Number
              </Label>
              <Input
                id="phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="+1 (555) 123-4567"
              />
            </div>
            
            <div>
              <Label htmlFor="password" className="flex items-center gap-2 mb-2">
                <Key className="w-4 h-4" />
                Password *
              </Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Strong password (min 8 chars)"
              />
              <p className="text-sm text-slate-500 mt-1 flex items-center gap-1">
                <Info className="w-3 h-3" />
                Must contain uppercase, lowercase, and number
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg bg-slate-50">
                <div className="flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-green-600" />
                  <div>
                    <Label htmlFor="is_verified" className="cursor-pointer">Verified Badge</Label>
                    <p className="text-xs text-slate-500">Grant verified status to user</p>
                  </div>
                </div>
                <Switch
                  id="is_verified"
                  checked={formData.is_verified}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_verified: checked })}
                />
              </div>

              <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg bg-slate-50">
                <div className="flex items-center gap-3">
                  <UserCheck className="w-5 h-5 text-blue-600" />
                  <div>
                    <Label htmlFor="is_active" className="cursor-pointer">Active Status</Label>
                    <p className="text-xs text-slate-500">User can login to platform</p>
                  </div>
                </div>
                <Switch
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                />
              </div>

              <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg bg-slate-50">
                <div className="flex items-center gap-3">
                  <Crown className="w-5 h-5 text-amber-600" />
                  <div>
                    <Label htmlFor="is_premium" className="cursor-pointer">Premium Status</Label>
                    <p className="text-xs text-slate-500">Grant premium features access</p>
                  </div>
                </div>
                <Switch
                  id="is_premium"
                  checked={formData.is_premium}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_premium: checked })}
                />
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)} className="flex items-center gap-2">
              <XCircle className="w-4 h-4" />
              Cancel
            </Button>
            <Button onClick={handleCreateUser} className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              Create User
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* User Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              User Details
            </DialogTitle>
          </DialogHeader>
          
          {selectedUser && (
            <div className="space-y-6">
              {/* User Profile Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <User className="w-5 h-5" />
                    Profile Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                          {selectedUser.user?.username?.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg flex items-center gap-2">
                            {selectedUser.user?.username}
                            {selectedUser.user?.is_verified && (
                              <Badge className="bg-blue-500">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Verified
                              </Badge>
                            )}
                            {selectedUser.user?.is_premium && (
                              <Badge className="bg-amber-500">
                                <Crown className="w-3 h-3 mr-1" />
                                Premium
                              </Badge>
                            )}
                          </h3>
                          <p className="text-slate-600">{selectedUser.user?.full_name || 'No full name provided'}</p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-slate-500 flex items-center gap-2">
                            <Mail className="w-4 h-4" />
                            Email
                          </Label>
                          <p>{selectedUser.user?.email}</p>
                        </div>
                        <div className="space-y-2">
                          <Label className="text-slate-500 flex items-center gap-2">
                            <Phone className="w-4 h-4" />
                            Phone
                          </Label>
                          <p>{selectedUser.user?.phone || 'N/A'}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-slate-500">KYC Status</Label>
                          <div>{getKycBadge(selectedUser.user?.kyc_status)}</div>
                        </div>
                        <div className="space-y-2">
                          <Label className="text-slate-500">Account Status</Label>
                          <div>{getStatusBadge(selectedUser.user?.is_active)}</div>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label className="text-slate-500 flex items-center gap-2">
                          <Calendar className="w-4 h-4" />
                          Member Since
                        </Label>
                        <p>{new Date(selectedUser.user?.created_at).toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Wallet Information */}
              {selectedUser.wallet && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Wallet className="w-5 h-5" />
                      Wallet Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 border border-slate-200 rounded-lg">
                        <DollarSign className="w-8 h-8 text-green-500 mx-auto mb-2" />
                        <Label className="text-slate-500">Available Balance</Label>
                        <p className="text-2xl font-bold text-green-600 mt-1">
                          ${selectedUser.wallet.balance?.toFixed(2)}
                        </p>
                      </div>
                      <div className="text-center p-4 border border-slate-200 rounded-lg">
                        <Lock className="w-8 h-8 text-orange-500 mx-auto mb-2" />
                        <Label className="text-slate-500">Locked Balance</Label>
                        <p className="text-2xl font-bold text-orange-600 mt-1">
                          ${selectedUser.wallet.locked_balance?.toFixed(2)}
                        </p>
                      </div>
                      <div className="text-center p-4 border border-slate-200 rounded-lg">
                        <TrendingUp className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                        <Label className="text-slate-500">Total Balance</Label>
                        <p className="text-2xl font-bold text-blue-600 mt-1">
                          ${((selectedUser.wallet.balance || 0) + (selectedUser.wallet.locked_balance || 0)).toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Activity Stats */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Activity className="w-5 h-5" />
                    Activity Overview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 border border-slate-200 rounded-lg">
                      <BarChart3 className="w-6 h-6 text-purple-500 mx-auto mb-2" />
                      <Label className="text-slate-500">Total Transactions</Label>
                      <p className="text-xl font-bold text-purple-600 mt-1">
                        {selectedUser.transaction_count || 0}
                      </p>
                    </div>
                    <div className="text-center p-4 border border-slate-200 rounded-lg">
                      <PieChart className="w-6 h-6 text-blue-500 mx-auto mb-2" />
                      <Label className="text-slate-500">Active Stakings</Label>
                      <p className="text-xl font-bold text-blue-600 mt-1">
                        {selectedUser.staking_positions?.length || 0}
                      </p>
                    </div>
                    <div className="text-center p-4 border border-slate-200 rounded-lg">
                      <TrendingUp className="w-6 h-6 text-green-500 mx-auto mb-2" />
                      <Label className="text-slate-500">Active Investments</Label>
                      <p className="text-xl font-bold text-green-600 mt-1">
                        {selectedUser.investment_positions?.length || 0}
                      </p>
                    </div>
                    <div className="text-center p-4 border border-slate-200 rounded-lg">
                      <Star className="w-6 h-6 text-amber-500 mx-auto mb-2" />
                      <Label className="text-slate-500">Success Rate</Label>
                      <p className="text-xl font-bold text-amber-600 mt-1">
                        {selectedUser.success_rate || '0%'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailDialog(false)} className="flex items-center gap-2">
              <XCircle className="w-4 h-4" />
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Thêm các icon còn thiếu
const ChevronLeft = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

const ChevronRight = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

export default AdminUsers;