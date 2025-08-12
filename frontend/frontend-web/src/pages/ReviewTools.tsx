import React, { useState, useEffect } from 'react';
import api from '../api';

interface ReviewItem {
  id: number;
  type: 'document' | 'transaction' | 'project' | 'company';
  title: string;
  description: string;
  status: 'pending' | 'approved' | 'rejected' | 'needs_revision';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_to: string;
  created_at: string;
  due_date: string;
  reviewer_comments: string[];
  attachments: string[];
  metadata: Record<string, any>;
  confidence_score: number;
  ai_suggestions: string[];
  compliance_issues: string[];
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

interface ReviewWorkflow {
  id: number;
  name: string;
  description: string;
  steps: ReviewStep[];
  active: boolean;
  created_at: string;
}

interface ReviewStep {
  id: number;
  name: string;
  role: string;
  order: number;
  required: boolean;
  auto_approve: boolean;
  conditions: string[];
}

interface ReviewStats {
  total_pending: number;
  total_approved: number;
  total_rejected: number;
  total_needs_revision: number;
  average_review_time: number;
  compliance_score: number;
  risk_alerts: number;
  overdue_reviews: number;
}

const ReviewTools: React.FC = () => {
  const [reviewItems, setReviewItems] = useState<ReviewItem[]>([]);
  const [workflows, setWorkflows] = useState<ReviewWorkflow[]>([]);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [showWorkflowModal, setShowWorkflowModal] = useState(false);
  const [filter, setFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [reviewComment, setReviewComment] = useState('');
  const [reviewDecision, setReviewDecision] = useState<'approve' | 'reject' | 'needs_revision'>('approve');

  useEffect(() => {
    fetchReviewData();
  }, []);

  const fetchReviewData = async () => {
    try {
      setLoading(true);
      const [itemsRes, workflowsRes, statsRes] = await Promise.all([
        api.get('/review/items/'),
        api.get('/review/workflows/'),
        api.get('/review/stats/')
      ]);
      
      setReviewItems(itemsRes.data);
      setWorkflows(workflowsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching review data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async () => {
    if (!selectedItem || !reviewComment.trim()) return;

    try {
      await api.post(`/review/items/${selectedItem.id}/review`, {
        decision: reviewDecision,
        comment: reviewComment,
        timestamp: new Date().toISOString()
      });

      setShowReviewModal(false);
      setSelectedItem(null);
      setReviewComment('');
      setReviewDecision('approve');
      fetchReviewData();
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  const getFilteredItems = () => {
    let filtered = reviewItems;

    // Apply status filter
    if (filter !== 'all') {
      filtered = filtered.filter(item => item.status === filter);
    }

    // Apply priority filter
    if (priorityFilter) {
      filtered = filtered.filter(item => item.priority === priorityFilter);
    }

    // Apply type filter
    if (typeFilter) {
      filtered = filtered.filter(item => item.type === typeFilter);
    }

    // Apply search
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.assigned_to.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered.sort((a, b) => {
      // Sort by priority first, then by due date
      const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
      const aPriority = priorityOrder[a.priority as keyof typeof priorityOrder];
      const bPriority = priorityOrder[b.priority as keyof typeof priorityOrder];
      
      if (aPriority !== bPriority) {
        return bPriority - aPriority;
      }
      
      return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'needs_revision': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return 'bg-red-600 text-white';
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-green-100 text-green-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'document': return '📄';
      case 'transaction': return '💰';
      case 'project': return '📋';
      case 'company': return '🏢';
      default: return '📝';
    }
  };

  const isOverdue = (dueDate: string) => {
    return new Date(dueDate) < new Date();
  };

  const filteredItems = getFilteredItems();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Review & Approval Tools</h1>
          <p className="text-gray-600 mt-1">Quality assurance and compliance review system</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowWorkflowModal(true)}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Manage Workflows
          </button>
          <button
            onClick={() => api.post('/review/items/bulk-assign')}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Auto-Assign Reviews
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <span className="text-blue-600 text-xl">⏳</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Pending Reviews</p>
                <p className="text-lg font-semibold text-gray-900">{stats.total_pending}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <span className="text-green-600 text-xl">✅</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Approved</p>
                <p className="text-lg font-semibold text-gray-900">{stats.total_approved}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <span className="text-yellow-600 text-xl">⚠️</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Compliance Score</p>
                <p className="text-lg font-semibold text-gray-900">{stats.compliance_score}%</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <span className="text-red-600 text-xl">🚨</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Risk Alerts</p>
                <p className="text-lg font-semibold text-gray-900">{stats.risk_alerts}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="needs_revision">Needs Revision</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="document">Document</option>
              <option value="transaction">Transaction</option>
              <option value="project">Project</option>
              <option value="company">Company</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search reviews..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setFilter('all');
                setPriorityFilter('');
                setTypeFilter('');
                setSearchTerm('');
              }}
              className="w-full bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Review Items List */}
      <div className="space-y-4">
        {filteredItems.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-sm text-center">
            <div className="text-gray-400 text-6xl mb-4">📋</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No review items found</h3>
            <p className="text-gray-600">All caught up with reviews!</p>
          </div>
        ) : (
          filteredItems.map((item) => (
            <div
              key={item.id}
              className={`bg-white p-6 rounded-lg shadow-sm border-l-4 ${
                isOverdue(item.due_date) ? 'border-red-500' : 'border-blue-500'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="flex-shrink-0">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{getTypeIcon(item.type)}</span>
                      <div className={`w-3 h-3 rounded-full ${getPriorityColor(item.priority)}`}></div>
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{item.title}</h3>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                        {item.status.replace('_', ' ')}
                      </span>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskColor(item.risk_level)}`}>
                        {item.risk_level} Risk
                      </span>
                      {isOverdue(item.due_date) && (
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                          Overdue
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">{item.description}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500">
                      <div>
                        <strong>Assigned to:</strong> {item.assigned_to}
                      </div>
                      <div>
                        <strong>Due:</strong> {new Date(item.due_date).toLocaleDateString()}
                      </div>
                      <div>
                        <strong>Confidence:</strong> {item.confidence_score}%
                      </div>
                      <div>
                        <strong>Created:</strong> {new Date(item.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    {item.ai_suggestions.length > 0 && (
                      <div className="mt-3">
                        <strong className="text-sm text-gray-700">AI Suggestions:</strong>
                        <ul className="mt-1 space-y-1">
                          {item.ai_suggestions.slice(0, 3).map((suggestion, index) => (
                            <li key={index} className="text-sm text-gray-600 flex items-center">
                              <span className="text-blue-500 mr-2">💡</span>
                              {suggestion}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {item.compliance_issues.length > 0 && (
                      <div className="mt-3">
                        <strong className="text-sm text-red-700">Compliance Issues:</strong>
                        <ul className="mt-1 space-y-1">
                          {item.compliance_issues.slice(0, 3).map((issue, index) => (
                            <li key={index} className="text-sm text-red-600 flex items-center">
                              <span className="text-red-500 mr-2">⚠️</span>
                              {issue}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {item.reviewer_comments.length > 0 && (
                      <div className="mt-3">
                        <strong className="text-sm text-gray-700">Review Comments:</strong>
                        <div className="mt-1 space-y-1">
                          {item.reviewer_comments.slice(-2).map((comment, index) => (
                            <div key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                              {comment}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={() => {
                      setSelectedItem(item);
                      setShowReviewModal(true);
                    }}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors"
                  >
                    Review
                  </button>
                  <button
                    onClick={() => window.open(`/review/items/${item.id}/details`, '_blank')}
                    className="bg-gray-600 text-white px-4 py-2 rounded-md text-sm hover:bg-gray-700 transition-colors"
                  >
                    Details
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Review Modal */}
      {showReviewModal && selectedItem && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Review Item</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Decision</label>
                  <select
                    value={reviewDecision}
                    onChange={(e) => setReviewDecision(e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="approve">Approve</option>
                    <option value="reject">Reject</option>
                    <option value="needs_revision">Needs Revision</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Review Comment</label>
                  <textarea
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Add your review comments..."
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowReviewModal(false);
                    setSelectedItem(null);
                    setReviewComment('');
                    setReviewDecision('approve');
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={handleReview}
                  disabled={!reviewComment.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit Review
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Workflow Management Modal */}
      {showWorkflowModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-3/4 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Review Workflows</h3>
              
              <div className="space-y-4">
                {workflows.map((workflow) => (
                  <div key={workflow.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-gray-900">{workflow.name}</h4>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          workflow.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {workflow.active ? 'Active' : 'Inactive'}
                        </span>
                        <button className="text-blue-600 hover:text-blue-800 text-sm">Edit</button>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{workflow.description}</p>
                    <div className="space-y-2">
                      {workflow.steps.map((step) => (
                        <div key={step.id} className="flex items-center space-x-3 text-sm">
                          <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium">
                            {step.order}
                          </span>
                          <span className="font-medium">{step.name}</span>
                          <span className="text-gray-500">({step.role})</span>
                          {step.required && <span className="text-red-500 text-xs">Required</span>}
                          {step.auto_approve && <span className="text-green-500 text-xs">Auto-approve</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-end mt-6">
                <button
                  type="button"
                  onClick={() => setShowWorkflowModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReviewTools; 