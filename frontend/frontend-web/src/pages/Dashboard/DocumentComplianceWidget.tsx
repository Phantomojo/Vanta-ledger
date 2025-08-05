import React, { useEffect, useState } from 'react';
import api from '../../api';

interface Document {
  id: string;
  title?: string;
  filename: string;
  type?: string;
  project_id?: string;
  company_id?: string;
  upload_date: string;
  size: number;
  status: 'processed' | 'pending_review' | 'approved' | 'rejected' | 'expired' | 'analyzed';
}

interface Project {
  id: string;
  name: string;
  company_id: string;
}

interface Company {
  id: string;
  name: string;
}

const DocumentComplianceWidget: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [documentsRes, projectsRes, companiesRes] = await Promise.all([
          api.get<any>('/upload/documents'),
          api.get<Project[]>('/projects/'),
          api.get<Company[]>('/companies/')
        ]);

        // Handle the response structure from the backend
        const documentsData = documentsRes.data.documents || documentsRes.data || [];
        setDocuments(documentsData);
        setProjects(projectsRes.data);
        setCompanies(companiesRes.data);
      } catch (err: any) {
        setError('Failed to load document compliance data.');
        console.error('Error fetching documents:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'invoice':
        return (
          <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        );
      case 'contract':
        return (
          <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        );
      case 'certificate':
        return (
          <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
        );
      case 'tender':
        return (
          <div className="w-8 h-8 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        );
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900';
      case 'processed':
        return 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900';
      case 'pending_review':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900';
      case 'rejected':
        return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900';
      case 'expired':
        return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'approved':
        return 'Approved';
      case 'processed':
        return 'Processed';
      case 'pending_review':
        return 'Pending Review';
      case 'rejected':
        return 'Rejected';
      case 'expired':
        return 'Expired';
      default:
        return status;
    }
  };

  const getDocumentTypeLabel = (type: string) => {
    switch (type) {
      case 'invoice':
        return 'Invoice';
      case 'contract':
        return 'Contract';
      case 'certificate':
        return 'Certificate';
      case 'tender':
        return 'Tender';
      case 'receipt':
        return 'Receipt';
      case 'tax_document':
        return 'Tax Document';
      default:
        return type;
    }
  };

  const getProjectName = (projectId?: string): string => {
    if (!projectId) return 'Unknown Project';
    const project = projects.find(p => p.id === projectId);
    return project?.name || 'Unknown Project';
  };

  const getCompanyName = (projectId?: string): string => {
    if (!projectId) return 'Unknown Company';
    const project = projects.find(p => p.id === projectId);
    if (!project) return 'Unknown Company';
    
    const company = companies.find(c => c.id === project.company_id);
    return company?.name || 'Unknown Company';
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-KE', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const getComplianceStats = () => {
    // Ensure documents is always an array
    const docsArray = Array.isArray(documents) ? documents : [];
    
    const stats = {
      total: docsArray.length,
      approved: docsArray.filter(d => d.status === 'approved').length,
      pending: docsArray.filter(d => d.status === 'pending_review').length,
      expired: docsArray.filter(d => d.status === 'expired').length,
      rejected: docsArray.filter(d => d.status === 'rejected').length
    };

    return {
      ...stats,
      complianceRate: stats.total > 0 ? Math.round((stats.approved / stats.total) * 100) : 0
    };
  };

  const getAlerts = () => {
    const alerts = [];
    
    // Ensure documents is always an array
    const docsArray = Array.isArray(documents) ? documents : [];
    
    const expiredDocs = docsArray.filter(d => d.status === 'expired');
    if (expiredDocs.length > 0) {
      alerts.push({
        type: 'error',
        message: `${expiredDocs.length} document(s) expired`,
        count: expiredDocs.length
      });
    }

    const pendingDocs = docsArray.filter(d => d.status === 'pending_review');
    if (pendingDocs.length > 0) {
      alerts.push({
        type: 'warning',
        message: `${pendingDocs.length} document(s) pending review`,
        count: pendingDocs.length
      });
    }

    const rejectedDocs = docsArray.filter(d => d.status === 'rejected');
    if (rejectedDocs.length > 0) {
      alerts.push({
        type: 'error',
        message: `${rejectedDocs.length} document(s) rejected`,
        count: rejectedDocs.length
      });
    }

    return alerts;
  };

  const stats = getComplianceStats();
  const alerts = getAlerts();

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
              </div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 mb-2">
          <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-gray-600 dark:text-gray-400">{error}</p>
      </div>
    );
  }

  // Ensure documents is always an array for the length check
  const docsArray = Array.isArray(documents) ? documents : [];
  
  if (docsArray.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 mb-2">
          <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-gray-600 dark:text-gray-400">No documents found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Compliance Overview */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-4">Document Compliance Overview</h3>
        
        {/* Compliance Rate */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">Compliance Rate</span>
            <span className="text-sm font-medium text-gray-900 dark:text-white">{stats.complianceRate}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                stats.complianceRate >= 80 ? 'bg-green-500' : 
                stats.complianceRate >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${stats.complianceRate}%` }}
            ></div>
          </div>
        </div>

        {/* Status Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="text-lg font-semibold text-green-600 dark:text-green-400">{stats.approved}</div>
            <div className="text-xs text-green-600 dark:text-green-400">Approved</div>
          </div>
          <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <div className="text-lg font-semibold text-yellow-600 dark:text-yellow-400">{stats.pending}</div>
            <div className="text-xs text-yellow-600 dark:text-yellow-400">Pending</div>
          </div>
          <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <div className="text-lg font-semibold text-red-600 dark:text-red-400">{stats.expired}</div>
            <div className="text-xs text-red-600 dark:text-red-400">Expired</div>
          </div>
          <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="text-lg font-semibold text-gray-600 dark:text-gray-400">{stats.total}</div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Total</div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Compliance Alerts</h3>
          <div className="space-y-2">
            {alerts.map((alert, index) => (
              <div 
                key={index} 
                className={`p-3 rounded-lg border-l-4 ${
                  alert.type === 'error' 
                    ? 'bg-red-50 dark:bg-red-900/20 border-red-400' 
                    : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-400'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <svg className={`w-4 h-4 ${
                    alert.type === 'error' ? 'text-red-500' : 'text-yellow-500'
                  }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className={`text-sm font-medium ${
                    alert.type === 'error' ? 'text-red-700 dark:text-red-300' : 'text-yellow-700 dark:text-yellow-300'
                  }`}>
                    {alert.message}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Documents */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">Recent Documents</h3>
          <button className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
            View All
          </button>
        </div>
        
        <div className="space-y-3">
          {docsArray
            .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
            .slice(0, 5)
            .map(document => (
              <div key={document.id} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                {getDocumentTypeIcon(document.type || 'unknown')}
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {document.title || document.filename}
                    </p>
                    <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(document.status)}`}>
                      {getStatusLabel(document.status)}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between mt-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {getDocumentTypeLabel(document.type || 'unknown')}
                      </span>
                      <span className="text-xs text-gray-400 dark:text-gray-500">•</span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {getProjectName(document.project_id)}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {formatDate(document.upload_date)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default DocumentComplianceWidget; 