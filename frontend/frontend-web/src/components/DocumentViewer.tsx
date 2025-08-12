import React, { useState, useEffect } from 'react';
import { Modal } from './ui/modal';
import api from '../api';

interface DocumentViewerProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
}

interface DocumentData {
  id: string;
  filename: string;
  title: string;
  file_type: string;
  upload_date: string;
  size: number;
  status: string;
  category: string;
  companies: string[];
  projects: string[];
  financial_data: any[];
  dates: string[];
  keywords: string[];
}

interface AnalysisData {
  extracted_data?: {
    amounts: number[];
    dates: string[];
    companies: string[];
    keywords: string[];
    entities: any;
  };
  confidence_scores?: {
    amounts: number;
    dates: number;
    companies: number;
    keywords: number;
  };
  analysis_timestamp?: string;
  content_length?: number;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ isOpen, onClose, documentId }) => {
  const [document, setDocument] = useState<DocumentData | null>(null);
  const [content, setContent] = useState<string>('');
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'content' | 'analysis' | 'metadata'>('content');

  useEffect(() => {
    if (isOpen && documentId) {
      loadDocument();
    }
  }, [isOpen, documentId]);

  const loadDocument = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/upload/documents/${documentId}`);
      const data = response.data;
      
      setDocument(data.document);
      setContent(data.content);
      setAnalysis(data.analysis);
    } catch (err: any) {
      setError('Failed to load document details');
      console.error('Error loading document:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    try {
      setLoading(true);
      const response = await api.post(`/upload/documents/${documentId}/analyze`);
      console.log('Analysis completed:', response.data);
      
      // Reload document to get updated analysis
      await loadDocument();
    } catch (err: any) {
      setError('Failed to analyze document');
      console.error('Error analyzing document:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
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

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="max-w-6xl max-h-[90vh] overflow-hidden">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            {document && getFileTypeIcon(document.file_type)}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {document?.title || document?.filename || 'Document Viewer'}
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {document && formatFileSize(document.size)} • {document && formatDate(document.upload_date)}
              </p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="px-4 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Re-analyze'}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Close
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('content')}
            className={`px-6 py-3 text-sm font-medium border-b-2 ${
              activeTab === 'content'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Content
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`px-6 py-3 text-sm font-medium border-b-2 ${
              activeTab === 'analysis'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Analysis
          </button>
          <button
            onClick={() => setActiveTab('metadata')}
            className={`px-6 py-3 text-sm font-medium border-b-2 ${
              activeTab === 'metadata'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Metadata
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : error ? (
            <div className="text-center text-red-600 dark:text-red-400">
              <p>{error}</p>
            </div>
          ) : (
            <>
              {/* Content Tab */}
              {activeTab === 'content' && (
                <div className="space-y-4">
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">Document Content</h3>
                    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md p-4 max-h-96 overflow-y-auto">
                      <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">
                        {content || 'No content available'}
                      </pre>
                    </div>
                  </div>
                </div>
              )}

              {/* Analysis Tab */}
              {activeTab === 'analysis' && (
                <div className="space-y-6">
                  {analysis?.extracted_data ? (
                    <>
                      {/* Amounts */}
                      {analysis.extracted_data.amounts && analysis.extracted_data.amounts.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                            Extracted Amounts
                            {analysis.confidence_scores && (
                              <span className="ml-2 text-sm text-gray-500">
                                (Confidence: {(analysis.confidence_scores.amounts * 100).toFixed(1)}%)
                              </span>
                            )}
                          </h3>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                            {analysis.extracted_data.amounts.map((amount, index) => (
                              <div key={index} className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-3 py-2 rounded-md text-center">
                                {amount.toLocaleString()} KES
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Dates */}
                      {analysis.extracted_data.dates && analysis.extracted_data.dates.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                            Extracted Dates
                            {analysis.confidence_scores && (
                              <span className="ml-2 text-sm text-gray-500">
                                (Confidence: {(analysis.confidence_scores.dates * 100).toFixed(1)}%)
                              </span>
                            )}
                          </h3>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                            {analysis.extracted_data.dates.map((date, index) => (
                              <div key={index} className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-2 rounded-md text-center">
                                {date}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Companies */}
                      {analysis.extracted_data.companies && analysis.extracted_data.companies.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                            Extracted Companies
                            {analysis.confidence_scores && (
                              <span className="ml-2 text-sm text-gray-500">
                                (Confidence: {(analysis.confidence_scores.companies * 100).toFixed(1)}%)
                              </span>
                            )}
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {analysis.extracted_data.companies.map((company, index) => (
                              <div key={index} className="bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 px-3 py-2 rounded-md">
                                {company}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Keywords */}
                      {analysis.extracted_data.keywords && analysis.extracted_data.keywords.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                            Extracted Keywords
                            {analysis.confidence_scores && (
                              <span className="ml-2 text-sm text-gray-500">
                                (Confidence: {(analysis.confidence_scores.keywords * 100).toFixed(1)}%)
                              </span>
                            )}
                          </h3>
                          <div className="flex flex-wrap gap-2">
                            {analysis.extracted_data.keywords.map((keyword, index) => (
                              <span key={index} className="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded-md text-sm">
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                      <p>No analysis data available. Click "Re-analyze" to process this document.</p>
                    </div>
                  )}
                </div>
              )}

              {/* Metadata Tab */}
              {activeTab === 'metadata' && document && (
                <div className="space-y-6">
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Document Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Title</label>
                        <p className="text-gray-900 dark:text-white">{document.title}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Filename</label>
                        <p className="text-gray-900 dark:text-white">{document.filename}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">File Type</label>
                        <p className="text-gray-900 dark:text-white">{document.file_type}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Size</label>
                        <p className="text-gray-900 dark:text-white">{formatFileSize(document.size)}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Status</label>
                        <p className="text-gray-900 dark:text-white">{document.status}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Category</label>
                        <p className="text-gray-900 dark:text-white">{document.category}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Upload Date</label>
                        <p className="text-gray-900 dark:text-white">{formatDate(document.upload_date)}</p>
                      </div>
                    </div>
                  </div>

                  {/* Companies */}
                  {document.companies && document.companies.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">Associated Companies</h3>
                      <div className="flex flex-wrap gap-2">
                        {document.companies.map((company, index) => (
                          <span key={index} className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-md">
                            {company}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Projects */}
                  {document.projects && document.projects.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">Associated Projects</h3>
                      <div className="flex flex-wrap gap-2">
                        {document.projects.map((project, index) => (
                          <span key={index} className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-3 py-1 rounded-md">
                            {project}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Keywords */}
                  {document.keywords && document.keywords.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">Keywords</h3>
                      <div className="flex flex-wrap gap-2">
                        {document.keywords.map((keyword, index) => (
                          <span key={index} className="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded-md text-sm">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default DocumentViewer; 