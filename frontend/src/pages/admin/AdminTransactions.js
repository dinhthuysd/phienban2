import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Receipt } from 'lucide-react';

const AdminTransactions = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Transaction History</h1>
        <p className="text-slate-600 mt-1">View all platform transactions</p>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <Receipt className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Transaction Management</h3>
            <p className="text-slate-600">Transaction history interface will be available here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminTransactions;