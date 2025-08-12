import React, { useState, useEffect } from "react";
import PageMeta from "../components/common/PageMeta";
import DocumentViewer from "../components/DocumentViewer";
import api from '../api';

interface Document {
  id: string;
  filename: string;
  upload_date: string;
  size: number;
  status: 'pending' | 'processed' | 'analyzed' | 'archived';
  title?: string;
  file_type?: string;
  company_id?: string;
  project_id?: string;
  category?: string;
  analyzed_at?: string;
  ocr_text?: string;
  extracted_data?: any;
}

interface Company {
  id: string;
  name: string;
}

interface Project {
  id: string;
  name: string;
}

interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  
  // Filter states
  const [selectedCompany, setSelectedCompany] = useState<string>('all');
  const [selectedProject, setSelectedProject] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [documentType, setDocumentType] = useState<string>('');
  const [keyword, setKeyword] = useState<string>('');

  // Upload states
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Document categories
  const categories = [
    'invoice', 'contract', 'receipt', 'bank_statement', 'tax_document',
    'certificate', 'tender', 'project_report', 'employee_record', 'other'
  ];

  // Add these state variables after the existing ones
  const [stats, setStats] = useState<any>(null);
  const [cacheInfo, setCacheInfo] = useState<any>(null);
  const [showStats, setShowStats] = useState(false);

  // Add state for document viewer
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [showDocumentViewer, setShowDocumentViewer] = useState(false);

  useEffect(() => {
    fetchData();
    fetchStats();
  }, []);

  const fetchData = async (page: number = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch documents, companies, and projects in parallel
      const [documentsRes, companiesRes, projectsRes] = await Promise.all([
        api.get<any>(`/upload/documents?page=${page}&limit=100`),
        api.get<Company[]>('/companies/'),
        api.get<Project[]>('/projects/')
      ]);

      // Handle the response structure from the backend
      const documentsData = documentsRes.data.documents || documentsRes.data || [];
      setDocuments(documentsData);
      setCompanies(companiesRes.data);
      setProjects(projectsRes.data);
      
      // Set pagination info
      if (documentsRes.data.pagination) {
        setPagination(documentsRes.data.pagination);
        setCurrentPage(page);
      }
    } catch (err: any) {
      setError('Failed to load documents.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const searchDocuments = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('query', searchTerm);
      if (documentType) params.append('document_type', documentType);
      if (selectedCompany !== 'all') params.append('company', selectedCompany);
      if (selectedProject !== 'all') params.append('project', selectedProject);
      if (keyword) params.append('keyword', keyword);
      
      const response = await api.get(`/upload/documents/search?${params.toString()}`);
      setDocuments(response.data.documents || []);
    } catch (err: any) {
      setError('Failed to search documents.');
      console.error('Error searching documents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setSelectedFiles(Array.from(event.target.files));
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      // Add metadata
      if (selectedCompany !== 'all') {
        formData.append('company_id', selectedCompany);
      }
      if (selectedProject !== 'all') {
        formData.append('project_id', selectedProject);
      }
      if (selectedCategory !== 'all') {
        formData.append('category', selectedCategory);
      }

      const response = await api.post('/upload/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(progress);
          }
        },
      });

      // Refresh documents list
      await fetchData();
      
      // Reset upload state
      setSelectedFiles([]);
      setUploadProgress(0);
      
      alert('Documents uploaded successfully!');
    } catch (err: any) {
      setError('Failed to upload documents.');
      console.error('Error uploading documents:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleViewDocument = async (documentId: string) => {
    setSelectedDocumentId(documentId);
    setShowDocumentViewer(true);
  };

  const handleCloseDocumentViewer = () => {
    setShowDocumentViewer(false);
    setSelectedDocumentId(null);
  };

  const handleAnalyzeDocument = async (documentId: string) => {
    try {
      const response = await api.post(`/upload/documents/${documentId}/analyze`);
      console.log('Analysis started:', response.data);
      alert(`Analysis started for document. ${response.data.message}`);
      // Refresh documents list to update status
      await fetchData();
    } catch (err: any) {
      setError('Failed to start document analysis.');
      console.error('Error analyzing document:', err);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await api.delete(`/upload/documents/${documentId}`);
      console.log('Document deleted:', response.data);
      alert('Document deleted successfully!');
      // Refresh documents list
      await fetchData();
    } catch (err: any) {
      setError('Failed to delete document.');
      console.error('Error deleting document:', err);
    }
  };

  const getFilteredDocuments = () => {
    return documents.filter(document => {
      // Company filter
      if (selectedCompany !== 'all' && document.company_id?.toString() !== selectedCompany) {
        return false;
      }
      
      // Project filter
      if (selectedProject !== 'all' && document.project_id?.toString() !== selectedProject) {
        return false;
      }
      
      // Status filter
      if (selectedStatus !== 'all' && document.status !== selectedStatus) {
        return false;
      }
      
      // Category filter
      if (selectedCategory !== 'all' && document.category !== selectedCategory) {
        return false;
      }
      
      // Search term filter
      if (searchTerm && !(document.title || document.filename).toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      
      return true;
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300';
      case 'processed': return 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-300';
      case 'analyzed': return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300';
      case 'archived': return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-300';
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getFileTypeIcon = (fileType?: string) => {
    if (!fileType) {
      return (
        <svg className="w-8 h-8 text-gray-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
        </svg>
      );
    }
    const type = fileType.toLowerCase();
    if (type.includes('pdf')) {
      return (
        <svg className="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
        </svg>
      );
    } else if (type.includes('image')) {
      return (
        <svg className="w-8 h-8 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M8.5,13.5L11,16.5L14.5,12L19,18H5M21,19V5C21,3.89 20.1,3 19,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19Z" />
        </svg>
      );
    } else if (type.includes('word') || type.includes('doc')) {
      return (
        <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
          <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
        </svg>
      );
    } else {
      return (
        <svg className="w-8 h-8 text-gray-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
        </svg>
      );
    }
  };

  const filteredDocuments = getFilteredDocuments();

  // Add this function after fetchData
  const fetchStats = async () => {
    try {
      const response = await api.get('/documents/stats');
      setStats(response.data.stats);
      setCacheInfo(response.data.cache_info);
    } catch (err: any) {
      console.error('Error fetching stats:', err);
    }
  };

  const refreshCache = async () => {
    try {
      setLoading(true);
      const response = await api.post('/documents/refresh-cache');
      alert(`Cache refreshed! ${response.data.total_documents} documents loaded.`);
      await fetchData(currentPage);
      await fetchStats();
    } catch (err: any) {
      alert('Failed to refresh cache: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <>
      <PageMeta
        title="Documents | Vanta Ledger Dashboard"
        description="Upload, manage, and analyze documents with AI-powered extraction."
      />
      
      <div className="p-3 md:p-4 lg:p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Documents</h1>
          <p className="text-gray-600 dark:text-gray-400">Upload and manage documents with AI-powered analysis</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Upload Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Upload Documents</h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4 mb-4">
            {/* Company Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Company</label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">Select Company</option>
                {companies.map(company => (
                  <option key={company.id || `company-${company.name}`} value={company.id}>{company.name}</option>
                ))}
              </select>
            </div>

            {/* Project Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Project</label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">Select Project</option>
                {projects.map(project => (
                  <option key={project.id || `project-${project.name}`} value={project.id}>{project.name}</option>
                ))}
              </select>
            </div>

            {/* Category Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">Select Category</option>
                {categories.map(category => (
                  <option key={category || `category-${Math.random()}`} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>

            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Files</label>
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.txt"
              />
            </div>
          </div>

          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Selected Files:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {selectedFiles.map((file, index) => (
                  <div key={`file-${file.name}-${index}`} className="flex items-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
                    <svg className="w-4 h-4 text-gray-500 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                    </svg>
                    <span className="text-sm text-gray-700 dark:text-gray-300 truncate">{file.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upload Progress */}
          {uploading && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Uploading...</span>
                <span className="text-sm text-gray-500">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={selectedFiles.length === 0 || uploading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Upload Documents'}
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3 md:gap-4">
            {/* Company Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Company</label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">All Companies</option>
                {companies.map(company => (
                  <option key={company.id || `company-${company.name}`} value={company.id}>{company.name}</option>
                ))}
              </select>
            </div>

            {/* Project Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Project</label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">All Projects</option>
                {projects.map(project => (
                  <option key={project.id || `project-${project.name}`} value={project.id}>{project.name}</option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="processed">Processed</option>
                <option value="analyzed">Analyzed</option>
                <option value="archived">Archived</option>
              </select>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">All Categories</option>
                {categories.map(category => (
                  <option key={category || `category-${Math.random()}`} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>

            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Search</label>
              <input
                type="text"
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
        </div>

        {/* Statistics Panel */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Document Statistics</h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowStats(!showStats)}
                className="px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {showStats ? 'Hide Stats' : 'Show Stats'}
              </button>
              <button
                onClick={refreshCache}
                disabled={loading}
                className="px-3 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                Refresh Cache
              </button>
            </div>
          </div>
          
          {showStats && stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                <div className="text-2xl font-bold text-blue-600">{stats.total_documents?.toLocaleString()}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Documents</div>
              </div>
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                <div className="text-2xl font-bold text-green-600">{stats.total_size_mb?.toFixed(1)} MB</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Size</div>
              </div>
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                <div className="text-2xl font-bold text-purple-600">{Object.keys(stats.document_types || {}).length}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Document Types</div>
              </div>
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                <div className="text-2xl font-bold text-orange-600">{Object.keys(stats.companies || {}).length}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Companies</div>
              </div>
            </div>
          )}
          
          {showStats && cacheInfo && (
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-6">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Cache Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Last Updated:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">
                    {cacheInfo.last_updated ? new Date(cacheInfo.last_updated).toLocaleString() : 'Never'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Cache Duration:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">{cacheInfo.cache_duration}s</span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Cache Size:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">{cacheInfo.cache_size?.toLocaleString() || 'N/A'}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Documents Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4 md:gap-6">
          {filteredDocuments.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-gray-600 dark:text-gray-400">No documents found</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Upload some documents to get started</p>
            </div>
          ) : (
            filteredDocuments.map((document) => (
              <div key={document.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center">
                    {getFileTypeIcon(document.file_type)}
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate max-w-32">
                        {document.title || document.filename}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {formatFileSize(document.size)}
                      </p>
                    </div>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(document.status)}`}>
                    {document.status.charAt(0).toUpperCase() + document.status.slice(1)}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  {document.company_id && (
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      <span className="font-medium">Company:</span> {companies.find(c => c.id.toString() === document.company_id)?.name || 'Unknown'}
                    </div>
                  )}
                  {document.project_id && (
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      <span className="font-medium">Project:</span> {projects.find(p => p.id.toString() === document.project_id)?.name || 'Unknown'}
                    </div>
                  )}
                  {document.category && (
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      <span className="font-medium">Category:</span> {document.category.charAt(0).toUpperCase() + document.category.slice(1).replace('_', ' ')}
                    </div>
                  )}
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Uploaded:</span> {new Date(document.upload_date).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button 
                    onClick={() => handleViewDocument(document.id)}
                    className="flex-1 px-3 py-1 text-xs bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-300 dark:hover:bg-indigo-800"
                  >
                    View
                  </button>
                  <button 
                    onClick={() => handleAnalyzeDocument(document.id)}
                    className="flex-1 px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 dark:bg-green-900 dark:text-green-300 dark:hover:bg-green-800"
                  >
                    Analyze
                  </button>
                  <button 
                    onClick={() => handleDeleteDocument(document.id)}
                    className="flex-1 px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {pagination && pagination.pages > 1 && (
          <div className="mt-8 flex items-center justify-between">
            <div className="text-sm text-gray-700 dark:text-gray-300">
              Showing page {pagination.page} of {pagination.pages} ({pagination.total} total documents)
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => fetchData(pagination.page - 1)}
                disabled={pagination.page <= 1}
                className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700"
              >
                Previous
              </button>
              <span className="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                {pagination.page} / {pagination.pages}
              </span>
              <button
                onClick={() => fetchData(pagination.page + 1)}
                disabled={pagination.page >= pagination.pages}
                className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Document Viewer Modal */}
      {selectedDocumentId && (
        <DocumentViewer
          isOpen={showDocumentViewer}
          onClose={handleCloseDocumentViewer}
          documentId={selectedDocumentId}
        />
      )}
    </>
  );
};

export default Documents; 