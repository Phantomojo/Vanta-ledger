import React, { useState, useEffect } from "react";
import PageMeta from "../components/common/PageMeta";
import api from '../api';

interface DocumentAnalysis {
  id: number;
  document_id: number;
  document_title: string;
  analysis_type: 'ocr' | 'nlp' | 'extraction' | 'classification';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  extracted_data: {
    companies: string[];
    amounts: number[];
    dates: string[];
    keywords: string[];
    entities: { type: string; value: string }[];
  };
  confidence_score: number;
  created_at: string;
  completed_at?: string;
}

interface AnalysisResult {
  text: string;
  entities: { type: string; value: string; confidence: number }[];
  sentiment: 'positive' | 'negative' | 'neutral';
  summary: string;
  key_insights: string[];
}

const AiNlp: React.FC = () => {
  const [documentAnalyses, setDocumentAnalyses] = useState<DocumentAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<DocumentAnalysis | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  
  // Analysis states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [inputText, setInputText] = useState('');
  const [analysisType, setAnalysisType] = useState<'ocr' | 'nlp' | 'extraction' | 'classification'>('nlp');

  useEffect(() => {
    fetchDocumentAnalyses();
  }, []);

  const fetchDocumentAnalyses = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock data for now - replace with actual API call
      const mockAnalyses: DocumentAnalysis[] = [
        {
          id: 1,
          document_id: 1,
          document_title: "Invoice_2024_001.pdf",
          analysis_type: 'extraction',
          status: 'completed',
          extracted_data: {
            companies: ['Vanta Construction Ltd', 'Nairobi Builders Co'],
            amounts: [150000, 75000],
            dates: ['2024-01-15', '2024-01-20'],
            keywords: ['construction', 'payment', 'invoice', 'materials'],
            entities: [
              { type: 'COMPANY', value: 'Vanta Construction Ltd' },
              { type: 'AMOUNT', value: '150,000 KES' },
              { type: 'DATE', value: '2024-01-15' }
            ]
          },
          confidence_score: 0.92,
          created_at: '2024-01-15T10:30:00Z',
          completed_at: '2024-01-15T10:32:00Z'
        },
        {
          id: 2,
          document_id: 2,
          document_title: "Contract_Project_A.pdf",
          analysis_type: 'nlp',
          status: 'completed',
          extracted_data: {
            companies: ['Mombasa Developers'],
            amounts: [500000],
            dates: ['2024-02-01'],
            keywords: ['contract', 'agreement', 'project', 'terms'],
            entities: [
              { type: 'COMPANY', value: 'Mombasa Developers' },
              { type: 'PROJECT', value: 'Hotel Renovation' },
              { type: 'AMOUNT', value: '500,000 KES' }
            ]
          },
          confidence_score: 0.88,
          created_at: '2024-02-01T14:20:00Z',
          completed_at: '2024-02-01T14:25:00Z'
        },
        {
          id: 3,
          document_id: 3,
          document_title: "Receipt_Materials.pdf",
          analysis_type: 'ocr',
          status: 'processing',
          extracted_data: {
            companies: [],
            amounts: [],
            dates: [],
            keywords: [],
            entities: []
          },
          confidence_score: 0,
          created_at: '2024-02-15T09:15:00Z'
        }
      ];

      setDocumentAnalyses(mockAnalyses);
    } catch (err: any) {
      setError('Failed to load document analyses.');
      console.error('Error fetching analyses:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeText = async () => {
    if (!inputText.trim()) return;

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setAnalysisResult(null);

    try {
      // Simulate analysis progress
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Mock API call - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      clearInterval(progressInterval);
      setAnalysisProgress(100);

      // Mock result
      const mockResult: AnalysisResult = {
        text: inputText,
        entities: [
          { type: 'COMPANY', value: 'Vanta Construction', confidence: 0.95 },
          { type: 'AMOUNT', value: '150,000 KES', confidence: 0.92 },
          { type: 'DATE', value: '2024-01-15', confidence: 0.88 },
          { type: 'PROJECT', value: 'Office Complex', confidence: 0.85 }
        ],
        sentiment: 'positive',
        summary: 'This document appears to be a construction invoice with positive financial implications.',
        key_insights: [
          'High-value construction project identified',
          'Payment terms are favorable',
          'Project timeline is on track',
          'All required documentation is present'
        ]
      };

      setAnalysisResult(mockResult);
    } catch (err: any) {
      setError('Failed to analyze text.');
      console.error('Error analyzing text:', err);
    } finally {
      setIsAnalyzing(false);
      setAnalysisProgress(0);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300';
      case 'processing': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300';
      case 'pending': return 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-300';
      case 'failed': return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300';
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getAnalysisTypeIcon = (type: string) => {
    switch (type) {
      case 'ocr':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
          </svg>
        );
      case 'nlp':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8Z" />
          </svg>
        );
      case 'extraction':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
          </svg>
        );
      case 'classification':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8Z" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z" />
          </svg>
        );
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300';
      case 'negative': return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300';
      case 'neutral': return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-300';
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-300';
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
        title="AI/NLP Analysis | Vanta Ledger Dashboard"
        description="AI-powered document analysis, text extraction, and natural language processing."
      />
      
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">AI/NLP Analysis</h1>
          <p className="text-gray-600 dark:text-gray-400">AI-powered document analysis and text extraction</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Text Analysis Section */}
          <div className="space-y-6">
            {/* Real-time Text Analysis */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Real-time Text Analysis</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Analysis Type</label>
                  <select
                    value={analysisType}
                    onChange={(e) => setAnalysisType(e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="nlp">Natural Language Processing</option>
                    <option value="ocr">OCR Text Extraction</option>
                    <option value="extraction">Data Extraction</option>
                    <option value="classification">Document Classification</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Input Text</label>
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Enter text to analyze..."
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                {isAnalyzing && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Analyzing...</span>
                      <span className="text-sm text-gray-500">{analysisProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${analysisProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleAnalyzeText}
                  disabled={!inputText.trim() || isAnalyzing}
                  className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Text'}
                </button>
              </div>
            </div>

            {/* Analysis Results */}
            {analysisResult && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Analysis Results</h2>
                
                <div className="space-y-4">
                  {/* Sentiment */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sentiment</h3>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSentimentColor(analysisResult.sentiment)}`}>
                      {analysisResult.sentiment.charAt(0).toUpperCase() + analysisResult.sentiment.slice(1)}
                    </span>
                  </div>

                  {/* Summary */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Summary</h3>
                    <p className="text-sm text-gray-900 dark:text-white">{analysisResult.summary}</p>
                  </div>

                  {/* Key Insights */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Key Insights</h3>
                    <ul className="space-y-1">
                      {analysisResult.key_insights.map((insight, index) => (
                        <li key={index} className="text-sm text-gray-900 dark:text-white flex items-start">
                          <span className="text-indigo-600 mr-2">•</span>
                          {insight}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Entities */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Extracted Entities</h3>
                    <div className="grid grid-cols-2 gap-2">
                      {analysisResult.entities.map((entity, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">{entity.type}</span>
                          <span className="text-xs text-gray-900 dark:text-white">{entity.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Document Analysis History */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Document Analysis History</h2>
              
              <div className="space-y-4">
                {documentAnalyses.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-gray-400 mb-2">
                      <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">No document analyses found</p>
                  </div>
                ) : (
                  documentAnalyses.map((analysis) => (
                    <div key={analysis.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center">
                          <div className="p-1 bg-indigo-100 dark:bg-indigo-900 rounded mr-3">
                            {getAnalysisTypeIcon(analysis.analysis_type)}
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900 dark:text-white">{analysis.document_title}</h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              {analysis.analysis_type.toUpperCase()} • {new Date(analysis.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(analysis.status)}`}>
                          {analysis.status.charAt(0).toUpperCase() + analysis.status.slice(1)}
                        </span>
                      </div>

                      {analysis.status === 'completed' && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-500 dark:text-gray-400">Confidence Score</span>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {(analysis.confidence_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          
                          {analysis.extracted_data.companies.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Companies Found:</p>
                              <div className="flex flex-wrap gap-1">
                                {analysis.extracted_data.companies.map((company, index) => (
                                  <span key={index} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 rounded">
                                    {company}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {analysis.extracted_data.amounts.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Amounts Found:</p>
                              <div className="flex flex-wrap gap-1">
                                {analysis.extracted_data.amounts.map((amount, index) => (
                                  <span key={index} className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 rounded">
                                    {amount.toLocaleString()} KES
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      <div className="mt-3 flex space-x-2">
                        <button className="text-xs text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300">
                          View Details
                        </button>
                        <button className="text-xs text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300">
                          Re-analyze
                        </button>
                        <button className="text-xs text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* AI Capabilities */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">AI Capabilities</h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                  <div className="w-8 h-8 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <svg className="w-4 h-4 text-indigo-600 dark:text-indigo-300" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                    </svg>
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">OCR</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Text extraction from images</p>
                </div>

                <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <svg className="w-4 h-4 text-green-600 dark:text-green-300" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z" />
                    </svg>
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">NLP</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Natural language processing</p>
                </div>

                <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <div className="w-8 h-8 bg-yellow-100 dark:bg-yellow-900 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <svg className="w-4 h-4 text-yellow-600 dark:text-yellow-300" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                    </svg>
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Extraction</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Data extraction & parsing</p>
                </div>

                <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <svg className="w-4 h-4 text-purple-600 dark:text-purple-300" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z" />
                    </svg>
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Classification</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Document classification</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default AiNlp; 