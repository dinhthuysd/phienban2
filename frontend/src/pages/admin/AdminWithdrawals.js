import React, { useEffect, useState } from 'react';
import adminService from '../../services/adminService';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Check, X } from 'lucide-react';
import { useToast } from '../../hooks/use-toast';

const AdminWithdrawals = () => {
  const [withdrawals, setWithdrawals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const { toast } = useToast();

  useEffect(() => {
    fetchWithdrawals();
  }, [page]);

  const fetchWithdrawals = async () => {
    try {
      setLoading(true);
      const data = await adminService.getWithdrawals({ page, status_filter: 'pending' });
      setWithdrawals(data.withdrawals);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch withdrawals',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async (withdrawalId, approved) => {
    try {
      await adminService.processWithdrawal(withdrawalId, approved);
      toast({
        title: 'Success',
        description: `Withdrawal ${approved ? 'approved' : 'rejected'} successfully`,
      });
      fetchWithdrawals();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to process withdrawal',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Withdrawal Management</h1>
        <p className="text-slate-600 mt-1">Approve or reject withdrawal requests</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Pending Withdrawals</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : withdrawals.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-slate-500">No pending withdrawals</p>
            </div>
          ) : (
            <div className="space-y-4">
              {withdrawals.map((withdrawal) => (
                <div key={withdrawal.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <div>
                          <p className="font-semibold text-slate-900">{withdrawal.user?.email || 'N/A'}</p>
                          <p className="text-sm text-slate-500">@{withdrawal.user?.username || 'N/A'}</p>
                        </div>
                      </div>
                      <div className="mt-3 grid grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-slate-500">Amount</p>
                          <p className="font-semibold text-lg text-red-600">${withdrawal.amount}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">Method</p>
                          <p className="font-medium">{withdrawal.withdrawal_method}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">Address</p>
                          <p className="font-medium text-xs truncate">{withdrawal.withdrawal_address}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">Date</p>
                          <p className="font-medium">{new Date(withdrawal.created_at).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <Button
                        onClick={() => handleProcess(withdrawal.id, true)}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <Check className="w-4 h-4 mr-1" />
                        Approve
                      </Button>
                      <Button
                        onClick={() => handleProcess(withdrawal.id, false)}
                        variant="destructive"
                      >
                        <X className="w-4 h-4 mr-1" />
                        Reject
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminWithdrawals;