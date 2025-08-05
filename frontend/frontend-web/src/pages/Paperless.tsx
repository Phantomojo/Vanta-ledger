import React, { useState, useEffect } from 'react';
import api from '../api';

interface PaperlessDocument {
  id: number;
  title: string;
  content: string;
  created_date: string;
  modified_date: string;
  added_date: string;
  tags: string[];
  correspondent: string;
  document_type: string;
  storage_path: string;
  filename: string;
  archive_serial_number: string;
  original_filename: string;
  checksum: string;
  mime_type: string;
  file_size: number;
  thumbnail_url?: string;
  download_url?: string;
  preview_url?: string;
  ocr_status: 'pending' | 'processing' | 'completed' | 'failed';
  ocr_text?: string;
  suggestions: string[];
}

interface PaperlessTag {
  id: number;
  name: string;
  color: string;
  slug: string;
  document_count: number;
}

interface PaperlessCorrespondent {
  id: number;
  name: string;
  slug: string;
  document_count: number;
  last_correspondence: string;
}

interface PaperlessDocumentType {
  id: number;
  name: string;
  slug: string;
  document_count: number;
}

interface PaperlessStats {
  total_documents: number;
  documents_this_month: number;
  documents_this_week: number;
  documents_today: number;
  pending_ocr: number;
  failed_ocr: number;
  total_tags: number;
  total_correspondents: number;
  total_document_types: number;
  storage_used: number;
  storage_available: number;
}

const Paperless: React.FC = () => {
  const [documents, setDocuments] = useState<PaperlessDocument[]>([]);
  const [tags, setTags] = useState<PaperlessTag[]>([]);
  const [correspondents, setCorrespondents] = useState<PaperlessCorrespondent[]>([]);
  const [documentTypes, setDocumentTypes] = useState<PaperlessDocumentType[]>([]);
  const [stats, setStats] = useState<PaperlessStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTags, setSelectedTags] = useState<number[]>([]);
  const [selectedCorrespondent, setSelectedCorrespondent] = useState<number | null>(null);
  const [selectedDocumentType, setSelectedDocumentType] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState('added_date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  useEffect(() => {
    checkConnection();
    fetchData();
  }, []);

  const checkConnection = async () => {
    try {
      setConnectionStatus('checking');
      await api.get('/paperless/health');
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('disconnected');
      console.error('Paperless connection failed:', error);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const [docsRes, tagsRes, correspondentsRes, typesRes, statsRes] = await Promise.all([
        api.get('/paperless/documents/'),
        api.get('/paperless/tags/'),
        api.get('/paperless/correspondents/'),
        api.get('/paperless/document-types/'),
        api.get('/paperless/stats/')
      ]);
      
      // Handle the response structure from the backend
      const documentsData = docsRes.data.documents || docsRes.data || [];
      setDocuments(documentsData);
      setTags(tagsRes.data);
      setCorrespondents(correspondentsRes.data);
      setDocumentTypes(typesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching Paperless data:', error);
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

    try {
      setUploading(true);
      setUploadProgress(0);

      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const formData = new FormData();
        formData.append('file', file);

        await api.post('/paperless/upload/', formData, {
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
            setUploadProgress(progress);
          }
        });

        // Update progress for multiple files
        const fileProgress = ((i + 1) / selectedFiles.length) * 100;
        setUploadProgress(fileProgress);
      }

      setShowUploadModal(false);
      setSelectedFiles([]);
      setUploadProgress(0);
      fetchData(); // Refresh data after upload
    } catch (error) {
      console.error('Error uploading documents:', error);
      // Show user-friendly error message
      alert('Failed to upload documents. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const getFilteredDocuments = () => {
    // Ensure documents is always an array
    const docsArray = Array.isArray(documents) ? documents : [];
    let filtered = [...docsArray];

    // Apply search
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply tag filter
    if (selectedTags.length > 0) {
      filtered = filtered.filter(doc =>
        selectedTags.some(tagId => doc.tags.includes(tagId.toString()))
      );
    }

    // Apply correspondent filter
    if (selectedCorrespondent) {
      filtered = filtered.filter(doc => doc.correspondent === selectedCorrespondent.toString());
    }

    // Apply document type filter
    if (selectedDocumentType) {
      filtered = filtered.filter(doc => doc.document_type === selectedDocumentType.toString());
    }

    // Apply sorting - ensure filtered is still an array
    if (!Array.isArray(filtered)) {
      console.warn('Filtered is not an array, resetting to empty array');
      filtered = [];
    }
    
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'title':
          aValue = a.title;
          bValue = b.title;
          break;
        case 'created_date':
          aValue = new Date(a.created_date).getTime();
          bValue = new Date(b.created_date).getTime();
          break;
        case 'file_size':
          aValue = a.file_size;
          bValue = b.file_size;
          break;
        default:
          aValue = new Date(a.added_date).getTime();
          bValue = new Date(b.added_date).getTime();
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  };

  const getOcrStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const filteredDocuments = getFilteredDocuments();

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
          <h1 className="text-2xl font-bold text-gray-900">Paperless Integration</h1>
          <div className="flex items-center mt-2">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              connectionStatus === 'connected' ? 'bg-green-500' : 
              connectionStatus === 'checking' ? 'bg-yellow-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-600">
              {connectionStatus === 'connected' ? 'Connected to Paperless-ngx' :
               connectionStatus === 'checking' ? 'Checking connection...' : 'Disconnected'}
            </span>
          </div>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Upload Documents
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <span className="text-blue-600 text-xl">📄</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Total Documents</p>
                <p className="text-lg font-semibold text-gray-900">{stats.total_documents}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <span className="text-yellow-600 text-xl">⏳</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Pending OCR</p>
                <p className="text-lg font-semibold text-gray-900">{stats.pending_ocr}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <span className="text-green-600 text-xl">🏷️</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Tags</p>
                <p className="text-lg font-semibold text-gray-900">{stats.total_tags}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <span className="text-purple-600 text-xl">💾</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Storage Used</p>
                <p className="text-lg font-semibold text-gray-900">{formatFileSize(stats.storage_used)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
            <select
              multiple
              value={selectedTags.map(String)}
              onChange={(e) => {
                const values = Array.from(e.target.selectedOptions, option => parseInt(option.value));
                setSelectedTags(values);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {tags.map(tag => (
                <option key={tag.id} value={tag.id}>{tag.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Correspondent</label>
            <select
              value={selectedCorrespondent || ''}
              onChange={(e) => setSelectedCorrespondent(e.target.value ? parseInt(e.target.value) : null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Correspondents</option>
              {correspondents.map(corr => (
                <option key={corr.id} value={corr.id}>{corr.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
            <select
              value={selectedDocumentType || ''}
              onChange={(e) => setSelectedDocumentType(e.target.value ? parseInt(e.target.value) : null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              {documentTypes.map(type => (
                <option key={type.id} value={type.id}>{type.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="added_date">Date Added</option>
              <option value="created_date">Date Created</option>
              <option value="title">Title</option>
              <option value="file_size">File Size</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedTags([]);
                setSelectedCorrespondent(null);
                setSelectedDocumentType(null);
                setSortBy('added_date');
                setSortOrder('desc');
              }}
              className="w-full bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDocuments.map((document) => (
          <div key={document.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow">
            <div className="p-4">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-medium text-gray-900 truncate flex-1">{document.title}</h3>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getOcrStatusColor(document.ocr_status)}`}>
                  {document.ocr_status}
                </span>
              </div>
              
              <div className="space-y-2 text-sm text-gray-600">
                <p><strong>Filename:</strong> {document.original_filename}</p>
                <p><strong>Size:</strong> {formatFileSize(document.file_size)}</p>
                <p><strong>Type:</strong> {document.mime_type}</p>
                <p><strong>Added:</strong> {new Date(document.added_date).toLocaleDateString()}</p>
                {document.correspondent && (
                  <p><strong>From:</strong> {correspondents.find(c => c.id.toString() === document.correspondent)?.name}</p>
                )}
                {document.tags.length > 0 && (
                  <div>
                    <strong>Tags:</strong>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {document.tags.map(tagId => {
                        const tag = tags.find(t => t.id.toString() === tagId);
                        return tag ? (
                          <span
                            key={tagId}
                            className="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                            style={{ backgroundColor: tag.color + '20', color: tag.color }}
                          >
                            {tag.name}
                          </span>
                        ) : null;
                      })}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 flex space-x-2">
                {document.preview_url && (
                  <button
                    onClick={() => window.open(document.preview_url, '_blank')}
                    className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors"
                  >
                    Preview
                  </button>
                )}
                {document.download_url && (
                  <button
                    onClick={() => window.open(document.download_url, '_blank')}
                    className="flex-1 bg-green-600 text-white px-3 py-2 rounded-md text-sm hover:bg-green-700 transition-colors"
                  >
                    Download
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Documents to Paperless</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Select Files</label>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif"
                    onChange={handleFileSelect}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {selectedFiles.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Selected Files:</label>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {selectedFiles.map((file, index) => (
                        <li key={index}>{file.name} ({formatFileSize(file.size)})</li>
                      ))}
                    </ul>
                  </div>
                )}

                {uploading && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Upload Progress:</label>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{Math.round(uploadProgress)}%</p>
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFiles([]);
                    setUploadProgress(0);
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  disabled={uploading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={selectedFiles.length === 0 || uploading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Paperless; 