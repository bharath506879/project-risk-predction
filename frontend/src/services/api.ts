import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(config: ApiConfig) {
    this.client = axios.create(config);
    this.loadToken();
    this.setupInterceptors();
  }

  private loadToken(): void {
    this.token = localStorage.getItem('access_token');
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  logout(): void {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  // Auth endpoints
  async register(email: string, username: string, password: string, fullName?: string) {
    return this.client.post('/auth/register', { email, username, password, full_name: fullName });
  }

  async login(email: string, password: string) {
    return this.client.post('/auth/login', { email, password });
  }

  // Projects endpoints
  async createProject(projectData: any) {
    return this.client.post('/projects', projectData);
  }

  async getProjects() {
    return this.client.get('/projects');
  }

  async getProject(id: number) {
    return this.client.get(`/projects/${id}`);
  }

  async deleteProject(id: number) {
    return this.client.delete(`/projects/${id}`);
  }

  // Risk assessment endpoints
  async calculateManualRisk(riskData: any) {
    return this.client.post('/risk/manual', riskData);
  }

  async analyzeUrl(url: string, category: string) {
    return this.client.post('/risk/url-scan', { url, project_category: category });
  }

  // Analytics endpoints
  async getAnalyticsSummary() {
    return this.client.get('/analytics/summary');
  }

  async getRiskTrends(periods?: number) {
    return this.client.get('/analytics/trends', { params: { periods } });
  }

  async getFactorAnalysis() {
    return this.client.get('/analytics/factors');
  }
}

export const apiClient = new ApiClient({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});
