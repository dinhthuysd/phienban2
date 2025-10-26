import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { FileCheck } from 'lucide-react';

const AdminLogs = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Audit Logs</h1>
        <p className="text-slate-600 mt-1">View system audit logs and activities</p>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
              <FileCheck className="w-8 h-8 text-orange-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Audit Log System</h3>
            <p className="text-slate-600">Audit log viewer will be available here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminLogs;