const API_BASE_URL = 'http://localhost:8000/dmcp';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  errors?: Array<{ msg: string }>;
}

export interface Datasource {
  id: string;
  name: string;
  database_type: string;
  host?: string;
  port?: string;
  database: string;
  username?: string;
  created_at: string;
}

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('dmcp_bearer_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = this.getAuthHeaders();

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw error;
    }
  }

  // Datasource methods
  async getDatasources(): Promise<Datasource[]> {
    const response = await this.makeRequest<Datasource[]>('/datasources');
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.errors?.[0]?.msg || 'Failed to load datasources');
  }

  async testDatasourceConnection(datasourceId: string): Promise<boolean> {
    const response = await this.makeRequest(`/datasources/${datasourceId}/test`, {
      method: 'POST',
    });
    return response.success;
  }

  // Authentication methods
  isAuthenticated(): boolean {
    return !!localStorage.getItem('dmcp_bearer_token');
  }

  getToken(): string | null {
    return localStorage.getItem('dmcp_bearer_token');
  }

  setToken(token: string): void {
    localStorage.setItem('dmcp_bearer_token', token);
  }

  clearToken(): void {
    localStorage.removeItem('dmcp_bearer_token');
  }
}

export const apiService = new ApiService();
