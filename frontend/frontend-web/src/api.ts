import axios, { AxiosResponse, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = 'http://localhost:8500'; // Vanta Ledger Backend

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token if available
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('jwt_token');
  if (token && config.headers) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Global error handler
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: any) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('jwt_token');
      window.location.href = '/signin';
    }
    
    // Handle other errors
    if (error.response && error.response.status >= 500) {
      console.error('Server error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

// Authentication functions
export const loginUser = async (username: string, password: string) => {
  try {
    // Use simple auth endpoint with local MongoDB backend
    const response = await api.post('/simple-auth', null, {
      params: { username, password }
    });
    
    if (response.data.access_token) {
      return {
        access_token: response.data.access_token,
        user: { username: username }
      };
    } else {
      throw new Error('Login failed - no token received');
    }
  } catch (error: any) {
    throw new Error("Authentication failed. Please check your credentials.");
  }
};

export const registerUser = async (userData: any) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Vanta Ledger API endpoints
export const vantaApi = {
  // Authentication
  login: (credentials: { username: string; password: string }) =>
    api.post('/simple-auth', null, { params: credentials }),
  register: (userData: any) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),

  // Companies
  getCompanies: () => api.get('/companies/'),
  createCompany: (companyData: any) => api.post('/companies/', companyData),
  updateCompany: (id: number, companyData: any) => api.put(`/companies/${id}`, companyData),
  deleteCompany: (id: number) => api.delete(`/companies/${id}`),

  // Projects
  getProjects: () => api.get('/projects/'),
  createProject: (projectData: any) => api.post('/projects/', projectData),
  updateProject: (id: number, projectData: any) => api.put(`/projects/${id}`, projectData),
  deleteProject: (id: number) => api.delete(`/projects/${id}`),

  // Documents
  getDocuments: () => api.get('/upload/documents'),
  uploadDocument: (formData: FormData) => api.post('/upload/document', formData),
  deleteDocument: (id: number) => api.delete(`/documents/${id}`),

  // Ledger
  getLedgerEntries: () => api.get('/ledger/'),
  createLedgerEntry: (entryData: any) => api.post('/ledger/', entryData),
  updateLedgerEntry: (id: number, entryData: any) => api.put(`/ledger/${id}`, entryData),
  deleteLedgerEntry: (id: number) => api.delete(`/ledger/${id}`),
  getLedgerSummary: (projectId?: number) => 
    api.get(projectId ? `/ledger/summary/${projectId}` : '/ledger/summary'),

  // Analytics
  getDashboardAnalytics: () => api.get('/analytics/dashboard'),
  getCompanyAnalytics: (companyId: number) => api.get(`/analytics/company/${companyId}`),

  // Extracted Data
  getExtractedData: (params?: {
    page?: number;
    limit?: number;
    min_confidence?: number;
    has_amount?: boolean;
    transaction_type?: string;
    category?: string;
  }) => api.get('/extracted-data/', { params }),
  
  getExtractedDataAnalytics: () => api.get('/extracted-data/analytics'),
  
  getExtractedDataStats: () => api.get('/extracted-data/stats'),
  
  exportExtractedData: (params?: {
    format?: 'json' | 'csv';
    min_confidence?: number;
  }) => api.get('/extracted-data/export', { params }),

  // Health check
  healthCheck: () => api.get('/health'),
};

export default api; 