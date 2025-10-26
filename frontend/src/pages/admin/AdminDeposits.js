import React, { useEffect, useState } from 'react';
import adminService from '../../services/adminService';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Check, X } from 'lucide-react';
import { useToast } from '../../hooks/use-toast';

const AdminDeposits = () => {
  const [deposits, setDeposits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const { toast } = useToast();

  useEffect(() => {
    fetchDeposits();
  }, [page]);

  const fetchDeposits = async () => {
    try {
      setLoading(true);
      const data = await adminService.getDeposits({ page, status_filter: 'pending' });
      setDeposits(data.deposits);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch deposits',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async (depositId, approved) => {
    try {
      await adminService.processDeposit(depositId, approved);
      toast({
        title: 'Success',
        description: `Deposit ${approved ? 'approved' : 'rejected'} successfully`,
      });
      fetchDeposits();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to process deposit',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Deposit Management</h1>
        <p className="text-slate-600 mt-1">Approve or reject deposit requests</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Pending Deposits</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : deposits.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-slate-500">No pending deposits</p>
            </div>
          ) : (
            <div className="space-y-4">
              {deposits.map((deposit) => (
                <div key={deposit.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <div>
                          <p className="font-semibold text-slate-900">{deposit.user?.email || 'N/A'}</p>
                          <p className="text-sm text-slate-500">@{deposit.user?.username || 'N/A'}</p>
                        </div>
                      </div>
                      <div className="mt-3 grid grid-cols-3 gap-4">
                        <div>
                          <p className="text-xs text-slate-500">Amount</p>
                          <p className="font-semibold text-lg text-green-600">${deposit.amount}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">Payment Method</p>
                          <p className="font-medium">{deposit.payment_method}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">Date</p>
                          <p className="font-medium">{new Date(deposit.created_at).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <Button
                        onClick={() => handleProcess(deposit.id, true)}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <Check className="w-4 h-4 mr-1" />
                        Approve
                      </Button>
                      <Button
                        onClick={() => handleProcess(deposit.id, false)}
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

export default AdminDeposits;