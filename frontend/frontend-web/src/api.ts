import axios, { AxiosResponse, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8500'; // Vanta Ledger Backend
const USE_TEST_ROUTES = ((import.meta as any).env?.VITE_USE_TEST_ROUTES || 'true').toLowerCase() === 'true';

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
    if (USE_TEST_ROUTES) {
      const response = await api.post('/simple-auth', null, {
        params: { username, password }
      });
      if (response.data.access_token) {
        return {
          access_token: response.data.access_token,
          user: { username }
        };
      }
      throw new Error('Login failed - no token received');
    } else {
      const form = new URLSearchParams();
      form.append('username', username);
      form.append('password', password);
      const response = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      if (response.data.access_token) {
        return {
          access_token: response.data.access_token,
          user: response.data.user || { username }
        };
      }
      throw new Error('Login failed - no token received');
    }
  } catch (error: any) {
    throw new Error('Authentication failed. Please check your credentials.');
  }
};

export const registerUser = async (userData: { username?: string; email: string; password: string; role?: string }) => {
  // Backend expects form-encoded fields via FastAPI Form(...)
  const form = new URLSearchParams();
  const username = userData.username || userData.email;
  form.append('username', username);
  form.append('email', userData.email);
  form.append('password', userData.password);
  if (userData.role) form.append('role', userData.role);
  const response = await api.post('/auth/register', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Vanta Ledger API endpoints
export const getApiBaseUrl = () => API_BASE_URL;

export const vantaApi = {
  // Authentication
  login: (credentials: { username: string; password: string }) => loginUser(credentials.username, credentials.password),
  register: (userData: any) => registerUser(userData),
  getCurrentUser: () => api.get('/auth/me'),

  // Companies
  getCompanies: () => api.get(USE_TEST_ROUTES ? '/test-companies' : '/companies'),
  createCompany: (companyData: any) => api.post('/companies/', companyData),
  updateCompany: (id: number, companyData: any) => api.put(`/companies/${id}`, companyData),
  deleteCompany: (id: number) => api.delete(`/companies/${id}`),

  // Projects
  getProjects: () => api.get('/projects/'),
  createProject: (projectData: any) => api.post('/projects/', projectData),
  updateProject: (id: number, projectData: any) => api.put(`/projects/${id}`, projectData),
  deleteProject: (id: number) => api.delete(`/projects/${id}`),

  // Documents
  getDocuments: () => api.get(USE_TEST_ROUTES ? '/test-documents' : '/upload/documents'),
  uploadDocument: (formData: FormData) => USE_TEST_ROUTES
    ? api.post('/test-upload-document', formData)
    : api.post('/upload/documents', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  deleteDocument: (id: number) => api.delete(`/documents/${id}`),

  // Ledger
  getLedgerEntries: () => api.get(USE_TEST_ROUTES ? '/test-ledger' : '/ledger'),
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

  // System health
  getSystemHealth: () => api.get('/health/system'),
  getSystemHealthAI: () => api.get('/health/system/ai'),
};

export const buildSystemHealthWsUrl = (intervalSeconds: number = 2) => {
  const base = getApiBaseUrl().replace(/^http/, 'ws');
  const sep = base.endsWith('/') ? '' : '';
  return `${base}/health/system/ws?interval_seconds=${intervalSeconds}`;
}

export default api; 