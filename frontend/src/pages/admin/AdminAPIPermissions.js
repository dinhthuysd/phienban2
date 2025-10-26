import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { useToast } from '../../hooks/use-toast';
import adminService from '../../services/adminService';
import { Shield, Plus, Trash2, Edit, CheckCircle, XCircle } from 'lucide-react';

const AdminAPIPermissions = () => {
  const { toast } = useToast();
  const [permissions, setPermissions] = useState([]);
  const [groupedPermissions, setGroupedPermissions] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: ''
  });

  useEffect(() => {
    fetchPermissions();
  }, []);

  const fetchPermissions = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAPIPermissions();
      setPermissions(data.permissions || []);
      setGroupedPermissions(data.grouped || {});
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to fetch API permissions',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePermission = async () => {
    try {
      await adminService.createAPIPermission(formData);
      setShowCreateDialog(false);
      fetchPermissions();
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        category: ''
      });
      
      toast({
        title: 'Success',
        description: 'API permission created successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create API permission',
        variant: 'destructive',
      });
    }
  };

  const handleToggleActive = async (permissionId, currentStatus) => {
    try {
      await adminService.updateAPIPermission(permissionId, {
        is_active: !currentStatus
      });
      fetchPermissions();
      toast({
        title: 'Success',
        description: 'Permission status updated',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update permission',
        variant: 'destructive',
      });
    }
  };

  const handleDeletePermission = async (permissionId) => {
    if (!window.confirm('Are you sure you want to delete this permission?')) {
      return;
    }
    
    try {
      await adminService.deleteAPIPermission(permissionId);
      fetchPermissions();
      toast({
        title: 'Success',
        description: 'API permission deleted successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete API permission',
        variant: 'destructive',
      });
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      documents: 'bg-blue-100 text-blue-800',
      wallet: 'bg-green-100 text-green-800',
      trading: 'bg-purple-100 text-purple-800',
      staking: 'bg-orange-100 text-orange-800',
      investment: 'bg-pink-100 text-pink-800',
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">API Permissions</h1>
          <p className="text-slate-600 mt-1">Manage API permission definitions</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Permission
        </Button>
      </div>

      {loading ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">Loading...</div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {Object.keys(groupedPermissions).length === 0 ? (
            <Card>
              <CardContent className="py-12">
                <div className="text-center text-slate-500">No API permissions found</div>
              </CardContent>
            </Card>
          ) : (
            Object.entries(groupedPermissions).map(([category, perms]) => (
              <Card key={category}>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="w-5 h-5 mr-2" />
                    {category.charAt(0).toUpperCase() + category.slice(1)} Permissions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {perms.map((perm) => (
                      <div
                        key={perm.id}
                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50"
                      >
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <Badge className={getCategoryColor(perm.category)}>
                              {perm.category}
                            </Badge>
                            <span className="font-mono font-medium text-slate-900">
                              {perm.name}
                            </span>
                            {perm.is_active ? (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            ) : (
                              <XCircle className="w-4 h-4 text-red-600" />
                            )}
                          </div>
                          <p className="text-sm text-slate-600 mt-1">{perm.description}</p>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleActive(perm.id, perm.is_active)}
                          >
                            {perm.is_active ? 'Deactivate' : 'Activate'}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeletePermission(perm.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Create Permission Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New API Permission</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Permission Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., documents:read"
              />
              <p className="text-sm text-slate-500 mt-1">Use format: category:action</p>
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description of what this permission allows"
              />
            </div>
            
            <div>
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g., documents, wallet, trading"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreatePermission}>Create Permission</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminAPIPermissions;
