import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Progress } from '../../components/ui/progress';
import { Shield, Check, X, Eye, Search, FileText, Calendar, User, TrendingUp, Clock, BarChart3, Image as ImageIcon, FileImage, History } from 'lucide-react';
import api from '../../services/api';

const AdminKYC = () => {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showTimelineModal, setShowTimelineModal] = useState(false);
  const [timelineData, setTimelineData] = useState(null);
  const [processingId, setProcessingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('pending');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [stats, setStats] = useState({
    overview: {},
    timeline: [],
    id_type_distribution: [],
    quality_distribution: {}
  });

  useEffect(() => {
    fetchSubmissions();
    fetchStatistics();
  }, [page, statusFilter]);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      const endpoint = statusFilter === 'pending' 
        ? `/admin/kyc/pending?page=${page}&limit=10`
        : `/admin/kyc/all?page=${page}&limit=10&status_filter=${statusFilter}`;
      
      const response = await api.get(endpoint);
      setSubmissions(response.data.submissions || []);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error('Error fetching KYC submissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await api.get('/admin/kyc/statistics?days=30');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const fetchTimeline = async (kycId) => {
    try {
      const response = await api.get(`/admin/kyc/timeline/${kycId}`);
      setTimelineData(response.data);
      setShowTimelineModal(true);
    } catch (error) {
      console.error('Error fetching timeline:', error);
      alert('Failed to load timeline');
    }
  };

  const handleVerify = async (kycId, approved, note = '') => {
    try {
      setProcessingId(kycId);
      await api.put(`/admin/kyc/${kycId}/verify?approved=${approved}&admin_note=${encodeURIComponent(note)}`);
      
      await fetchSubmissions();
      await fetchStatistics();
      setShowModal(false);
      setSelectedSubmission(null);
      
      alert(`KYC ${approved ? 'approved' : 'rejected'} successfully!`);
    } catch (error) {
      console.error('Error verifying KYC:', error);
      alert('Error processing KYC. Please try again.');
    } finally {
      setProcessingId(null);
    }
  };

  const openModal = (submission) => {
    setSelectedSubmission(submission);
    setShowModal(true);
  };

  const filteredSubmissions = submissions.filter(sub => 
    sub.user?.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sub.user?.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sub.user?.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getQualityColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-blue-600 bg-blue-100';
    if (score >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getQualityLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Acceptable';
    return 'Poor';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">KYC Verification Management</h1>
        <p className="text-slate-600 mt-1">Review, verify, and monitor user identity documents</p>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview" data-testid="kyc-overview-tab">
            <BarChart3 className="w-4 h-4 mr-2" />
            Overview & Statistics
          </TabsTrigger>
          <TabsTrigger value="submissions" data-testid="kyc-submissions-tab">
            <FileText className="w-4 h-4 mr-2" />
            Submissions
          </TabsTrigger>
        </TabsList>

        {/* OVERVIEW TAB */}
        <TabsContent value="overview" className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card data-testid="kyc-stat-pending">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Pending</p>
                    <p className="text-3xl font-bold text-yellow-600 mt-1">{stats.overview?.pending || 0}</p>
                  </div>
                  <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                    <Clock className="w-6 h-6 text-yellow-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card data-testid="kyc-stat-approved">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Approved</p>
                    <p className="text-3xl font-bold text-green-600 mt-1">{stats.overview?.approved || 0}</p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <Check className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card data-testid="kyc-stat-rejected">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Rejected</p>
                    <p className="text-3xl font-bold text-red-600 mt-1">{stats.overview?.rejected || 0}</p>
                  </div>
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                    <X className="w-6 h-6 text-red-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card data-testid="kyc-stat-approval-rate">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Approval Rate</p>
                    <p className="text-3xl font-bold text-blue-600 mt-1">{stats.overview?.approval_rate || 0}%</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* ID Type Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">ID Type Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stats.id_type_distribution?.map((item, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium capitalize text-slate-700">
                          {item.type?.replace('_', ' ') || 'Unknown'}
                        </span>
                        <span className="text-slate-600">{item.count}</span>
                      </div>
                      <Progress 
                        value={(item.count / stats.overview?.total_submissions) * 100 || 0} 
                        className="h-2"
                      />
                    </div>
                  ))}
                  {stats.id_type_distribution?.length === 0 && (
                    <p className="text-sm text-slate-500 text-center py-4">No data available</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Quality Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Document Quality Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(stats.quality_distribution || {}).map(([level, count]) => (
                    <div key={level} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium capitalize text-slate-700">{level}</span>
                        <span className="text-slate-600">{count}</span>
                      </div>
                      <Progress 
                        value={(count / Math.max(...Object.values(stats.quality_distribution || {1: 1}))) * 100} 
                        className="h-2"
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Processing Time */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Processing Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-slate-50 rounded-lg">
                  <p className="text-sm text-slate-600 mb-1">Average Processing Time</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {stats.overview?.avg_processing_time_hours?.toFixed(1) || 0}h
                  </p>
                </div>
                <div className="text-center p-4 bg-slate-50 rounded-lg">
                  <p className="text-sm text-slate-600 mb-1">Min Processing Time</p>
                  <p className="text-2xl font-bold text-green-600">
                    {stats.processing_times?.min?.toFixed(1) || 0}h
                  </p>
                </div>
                <div className="text-center p-4 bg-slate-50 rounded-lg">
                  <p className="text-sm text-slate-600 mb-1">Max Processing Time</p>
                  <p className="text-2xl font-bold text-red-600">
                    {stats.processing_times?.max?.toFixed(1) || 0}h
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* SUBMISSIONS TAB */}
        <TabsContent value="submissions" className="space-y-4">
          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search by email, username, or name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="kyc-search-input"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setStatusFilter('pending')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  statusFilter === 'pending' 
                    ? 'bg-yellow-600 text-white' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
                data-testid="filter-pending-btn"
              >
                Pending
              </button>
              <button
                onClick={() => setStatusFilter('approved')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  statusFilter === 'approved' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
                data-testid="filter-approved-btn"
              >
                Approved
              </button>
              <button
                onClick={() => setStatusFilter('rejected')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  statusFilter === 'rejected' 
                    ? 'bg-red-600 text-white' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
                data-testid="filter-rejected-btn"
              >
                Rejected
              </button>
            </div>
          </div>

          {/* Submissions List */}
          <Card>
            <CardContent className="p-6">
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-slate-600">Loading submissions...</p>
                </div>
              ) : filteredSubmissions.length === 0 ? (
                <div className="text-center py-12">
                  <Shield className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-600">No {statusFilter} KYC submissions</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredSubmissions.map((submission) => (
                    <div
                      key={submission.id}
                      className="border border-slate-200 rounded-lg p-4 hover:border-blue-300 transition-all hover:shadow-sm"
                      data-testid={`kyc-submission-${submission.id}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                              <User className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-slate-900">
                                {submission.user?.full_name || 'N/A'}
                              </h3>
                              <p className="text-sm text-slate-600">
                                {submission.user?.email || 'N/A'}
                              </p>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
                            <div className="flex items-center gap-2 text-slate-600">
                              <FileText className="w-4 h-4" />
                              <span className="capitalize">{submission.id_type?.replace('_', ' ') || 'N/A'}</span>
                            </div>
                            <div className="flex items-center gap-2 text-slate-600">
                              <ImageIcon className="w-4 h-4" />
                              <span>{submission.file_ids?.length || 0} files</span>
                            </div>
                            <div className="flex items-center gap-2 text-slate-600">
                              <Calendar className="w-4 h-4" />
                              <span>{submission.created_at ? new Date(submission.created_at).toLocaleDateString() : 'N/A'}</span>
                            </div>
                            {submission.analysis?.validation_score && (
                              <div className="flex items-center gap-2">
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getQualityColor(submission.analysis.validation_score)}`}>
                                  Score: {submission.analysis.validation_score}%
                                </span>
                              </div>
                            )}
                          </div>

                          {/* Analysis Info */}
                          {submission.analysis && (
                            <div className="mt-3 p-3 bg-slate-50 rounded-lg">
                              <p className="text-xs font-semibold text-slate-700 mb-2">Auto-Analysis Results:</p>
                              <div className="grid grid-cols-2 lg:grid-cols-3 gap-2 text-xs">
                                <div>
                                  <span className="text-slate-600">Quality: </span>
                                  <span className="font-medium">{getQualityLabel(submission.analysis.quality_analysis?.quality_score || 0)}</span>
                                </div>
                                <div>
                                  <span className="text-slate-600">Auto-Approved: </span>
                                  <span className={`font-medium ${submission.analysis.auto_approved ? 'text-green-600' : 'text-orange-600'}`}>
                                    {submission.analysis.auto_approved ? 'Yes' : 'No'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-slate-600">Validation: </span>
                                  <span className="font-medium">{submission.analysis.validation_score}%</span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="flex flex-col gap-2 ml-4">
                          <button
                            onClick={() => fetchTimeline(submission.id)}
                            className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors flex items-center gap-2 whitespace-nowrap"
                            data-testid={`timeline-btn-${submission.id}`}
                          >
                            <History className="w-4 h-4" />
                            Timeline
                          </button>
                          {statusFilter === 'pending' && (
                            <button
                              onClick={() => openModal(submission)}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 whitespace-nowrap"
                              data-testid={`review-btn-${submission.id}`}
                            >
                              <Eye className="w-4 h-4" />
                              Review
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-6">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="px-4 py-2 text-slate-600">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Review Modal */}
      {showModal && selectedSubmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" data-testid="review-modal">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-200">
              <h2 className="text-2xl font-bold text-slate-900">Review KYC Submission</h2>
            </div>

            <div className="p-6 space-y-6">
              {/* User Info */}
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">User Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-slate-600">Full Name</p>
                    <p className="font-medium text-slate-900">{selectedSubmission.user?.full_name || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Email</p>
                    <p className="font-medium text-slate-900">{selectedSubmission.user?.email || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Username</p>
                    <p className="font-medium text-slate-900">{selectedSubmission.user?.username || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Submission Date</p>
                    <p className="font-medium text-slate-900">
                      {selectedSubmission.created_at ? new Date(selectedSubmission.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Auto-Analysis Results */}
              {selectedSubmission.analysis && (
                <div>
                  <h3 className="font-semibold text-slate-900 mb-3">Auto-Analysis Results</h3>
                  <div className="bg-slate-50 rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Overall Validation Score</span>
                      <span className={`text-lg font-bold ${getQualityColor(selectedSubmission.analysis.validation_score)}`}>
                        {selectedSubmission.analysis.validation_score}%
                      </span>
                    </div>
                    <Progress value={selectedSubmission.analysis.validation_score} className="h-2" />
                    
                    {selectedSubmission.analysis.quality_analysis && (
                      <div className="grid grid-cols-2 gap-3 mt-3 text-sm">
                        <div>
                          <p className="text-slate-600">Image Quality</p>
                          <p className="font-medium">{selectedSubmission.analysis.quality_analysis.quality_level || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-slate-600">Quality Score</p>
                          <p className="font-medium">{selectedSubmission.analysis.quality_analysis.quality_score}%</p>
                        </div>
                      </div>
                    )}

                    {selectedSubmission.analysis.auto_approved && (
                      <div className="mt-3 p-2 bg-green-100 border border-green-200 rounded text-sm text-green-800">
                        ✓ This submission passed auto-approval thresholds
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Document Info */}
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Document Information</h3>
                <div className="bg-slate-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-slate-600" />
                    <span className="font-medium text-slate-900 capitalize">
                      ID Type: {selectedSubmission.id_type?.replace('_', ' ') || 'N/A'}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">
                    Files uploaded: {selectedSubmission.file_ids?.length || 0} document(s)
                  </p>
                </div>
              </div>

              {/* Admin Note */}
              <div>
                <label className="block text-sm font-medium text-slate-900 mb-2">
                  Admin Note (Optional)
                </label>
                <textarea
                  id="admin-note"
                  rows="3"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Add a note about this verification..."
                  data-testid="admin-note-input"
                ></textarea>
              </div>
            </div>

            {/* Actions */}
            <div className="p-6 border-t border-slate-200 flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowModal(false);
                  setSelectedSubmission(null);
                }}
                className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                disabled={processingId}
                data-testid="cancel-review-btn"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const note = document.getElementById('admin-note').value;
                  handleVerify(selectedSubmission.id, false, note);
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                disabled={processingId === selectedSubmission.id}
                data-testid="reject-kyc-btn"
              >
                <X className="w-4 h-4" />
                {processingId === selectedSubmission.id ? 'Processing...' : 'Reject'}
              </button>
              <button
                onClick={() => {
                  const note = document.getElementById('admin-note').value;
                  handleVerify(selectedSubmission.id, true, note);
                }}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                disabled={processingId === selectedSubmission.id}
                data-testid="approve-kyc-btn"
              >
                <Check className="w-4 h-4" />
                {processingId === selectedSubmission.id ? 'Processing...' : 'Approve'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Timeline Modal */}
      {showTimelineModal && timelineData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" data-testid="timeline-modal">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-200">
              <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                <History className="w-6 h-6 text-blue-600" />
                KYC Submission Timeline
              </h2>
              <p className="text-sm text-slate-600 mt-1">Status: <span className="font-medium capitalize">{timelineData.current_status}</span></p>
            </div>

            <div className="p-6">
              <div className="relative">
                {/* Timeline Line */}
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-200"></div>

                {/* Timeline Events */}
                <div className="space-y-6">
                  {timelineData.timeline?.map((event, idx) => (
                    <div key={idx} className="relative pl-14">
                      {/* Event Icon */}
                      <div className={`absolute left-0 w-12 h-12 rounded-full flex items-center justify-center ${
                        event.event === 'submitted' ? 'bg-blue-100' :
                        event.event === 'analyzed' ? 'bg-purple-100' :
                        event.event === 'approved' ? 'bg-green-100' :
                        event.event === 'rejected' ? 'bg-red-100' :
                        'bg-slate-100'
                      }`}>
                        {event.event === 'submitted' && <FileText className="w-5 h-5 text-blue-600" />}
                        {event.event === 'analyzed' && <Shield className="w-5 h-5 text-purple-600" />}
                        {event.event === 'approved' && <Check className="w-5 h-5 text-green-600" />}
                        {event.event === 'rejected' && <X className="w-5 h-5 text-red-600" />}
                        {!['submitted', 'analyzed', 'approved', 'rejected'].includes(event.event) && <Clock className="w-5 h-5 text-slate-600" />}
                      </div>

                      {/* Event Content */}
                      <div className="bg-slate-50 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-slate-900 capitalize">{event.event}</h4>
                          <span className="text-xs text-slate-500">
                            {event.timestamp ? new Date(event.timestamp).toLocaleString() : 'N/A'}
                          </span>
                        </div>
                        <p className="text-sm text-slate-600 mb-2">{event.description}</p>
                        {event.details && Object.keys(event.details).length > 0 && (
                          <div className="text-xs text-slate-500 space-y-1 mt-2 pt-2 border-t border-slate-200">
                            {Object.entries(event.details).map(([key, value]) => (
                              <div key={key}>
                                <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => {
                  setShowTimelineModal(false);
                  setTimelineData(null);
                }}
                className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
                data-testid="close-timeline-btn"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminKYC;