import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { FileText } from 'lucide-react';

const AdminDocuments = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Document Management</h1>
        <p className="text-slate-600 mt-1">Approve or reject uploaded documents</p>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
              <FileText className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Document Approval System</h3>
            <p className="text-slate-600">Document approval interface will be available here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDocuments;