import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { useToast } from '../../hooks/use-toast';
import adminService from '../../services/adminService';
import { Key, Plus, Trash2, Eye, EyeOff, Copy, Check } from 'lucide-react';

const AdminAPITokens = () => {
  const { toast } = useToast();
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showTokenDialog, setShowTokenDialog] = useState(false);
  const [newToken, setNewToken] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [copied, setCopied] = useState(false);
  
  const [formData, setFormData] = useState({
    user_id: '',
    name: '',
    permissions: [],
    expires_in_days: 30
  });

  useEffect(() => {
    fetchTokens();
    fetchPermissions();
  }, []);

  const fetchTokens = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAPITokens({ page: 1, limit: 100 });
      setTokens(data.tokens || []);
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to fetch API tokens',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchPermissions = async () => {
    try {
      const data = await adminService.getAPIPermissions();
      setPermissions(data.permissions || []);
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
    }
  };

  const handleCreateToken = async () => {
    try {
      const response = await adminService.createAPIToken(formData);
      setNewToken(response);
      setShowCreateDialog(false);
      setShowTokenDialog(true);
      fetchTokens();
      
      // Reset form
      setFormData({
        user_id: '',
        name: '',
        permissions: [],
        expires_in_days: 30
      });
      
      toast({
        title: 'Success',
        description: 'API token created successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create API token',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteToken = async (tokenId) => {
    if (!window.confirm('Are you sure you want to revoke this API token?')) {
      return;
    }
    
    try {
      await adminService.deleteAPIToken(tokenId);
      fetchTokens();
      toast({
        title: 'Success',
        description: 'API token revoked successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to revoke API token',
        variant: 'destructive',
      });
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast({
      title: 'Copied',
      description: 'API key copied to clipboard',
    });
  };

  const togglePermission = (permission) => {
    setFormData(prev => ({
      ...prev,
      permissions: prev.permissions.includes(permission)
        ? prev.permissions.filter(p => p !== permission)
        : [...prev.permissions, permission]
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">API Token Management</h1>
          <p className="text-slate-600 mt-1">Manage API access tokens for users</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Token
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Key className="w-5 h-5 mr-2" />
            API Tokens
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : tokens.length === 0 ? (
            <div className="text-center py-8 text-slate-500">No API tokens found</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Permissions</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Expires</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tokens.map((token) => (
                  <TableRow key={token.id}>
                    <TableCell className="font-medium">{token.name}</TableCell>
                    <TableCell>
                      {token.user ? (
                        <div>
                          <div className="font-medium">{token.user.username}</div>
                          <div className="text-sm text-slate-500">{token.user.email}</div>
                        </div>
                      ) : (
                        'N/A'
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {token.permissions.slice(0, 3).map((perm) => (
                          <Badge key={perm} variant="secondary" className="text-xs">
                            {perm}
                          </Badge>
                        ))}
                        {token.permissions.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{token.permissions.length - 3}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {token.is_active ? (
                        <Badge className="bg-green-500">Active</Badge>
                      ) : (
                        <Badge variant="destructive">Inactive</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {token.expires_at ? (
                        <span className="text-sm">{new Date(token.expires_at).toLocaleDateString()}</span>
                      ) : (
                        <span className="text-sm text-slate-500">Never</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{new Date(token.created_at).toLocaleDateString()}</span>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteToken(token.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Create Token Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New API Token</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="user_id">User ID</Label>
              <Input
                id="user_id"
                value={formData.user_id}
                onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                placeholder="Enter user ID"
              />
            </div>
            
            <div>
              <Label htmlFor="name">Token Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Production API Key"
              />
            </div>
            
            <div>
              <Label htmlFor="expires_in_days">Expires In (Days)</Label>
              <Input
                id="expires_in_days"
                type="number"
                value={formData.expires_in_days}
                onChange={(e) => setFormData({ ...formData, expires_in_days: parseInt(e.target.value) })}
                placeholder="30"
              />
              <p className="text-sm text-slate-500 mt-1">Leave as 0 for no expiration</p>
            </div>
            
            <div>
              <Label>Permissions</Label>
              <div className="grid grid-cols-2 gap-2 mt-2 max-h-48 overflow-y-auto border rounded-md p-3">
                {permissions.map((perm) => (
                  <div key={perm.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={perm.name}
                      checked={formData.permissions.includes(perm.name)}
                      onChange={() => togglePermission(perm.name)}
                      className="rounded border-gray-300"
                    />
                    <label htmlFor={perm.name} className="text-sm cursor-pointer">
                      {perm.name}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateToken}>Create Token</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Show Token Dialog */}
      <Dialog open={showTokenDialog} onOpenChange={setShowTokenDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>API Token Created</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800 font-medium">
                ⚠️ Important: Copy this token now. You won't be able to see it again!
              </p>
            </div>
            
            <div>
              <Label>API Key</Label>
              <div className="flex items-center space-x-2 mt-2">
                <Input
                  value={newToken?.api_key || ''}
                  readOnly
                  className="font-mono text-sm"
                />
                <Button
                  size="sm"
                  onClick={() => copyToClipboard(newToken?.api_key)}
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </Button>
              </div>
            </div>
            
            <div>
              <Label>Token ID</Label>
              <Input
                value={newToken?.token_id || ''}
                readOnly
                className="mt-2"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button onClick={() => {
              setShowTokenDialog(false);
              setNewToken(null);
            }}>
              Done
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminAPITokens;
