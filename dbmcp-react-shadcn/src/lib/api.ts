const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  expires_in_minutes: number;
}

export interface TokenGenerationResponse {
  success: boolean;
  data?: {
    token: string;
    expires_at: string;
    username: string;
  };
  errors?: Array<{ msg: string }>;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ChangePasswordResponse {
  success: boolean;
  message?: string;
  errors?: Array<{ msg: string }>;
}

export interface UserProfile {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  roles: string[];
  created_at: string;
  updated_at: string;
}

export interface UserProfileResponse {
  success: boolean;
  data?: UserProfile;
  errors?: Array<{ msg: string }>;
}

export interface DataSource {
  id: number;
  name: string;
  database_type: string;
  host: string;
  port: number;
  database: string;
  username: string;
  connection_string?: string;
  ssl_mode?: string;
  additional_params?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface DataSourceCreateRequest {
  name: string;
  database_type: string;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  connection_string?: string;
  ssl_mode?: string;
  additional_params?: Record<string, any>;
}

export interface DataSourceResponse {
  success: boolean;
  data?: DataSource;
  errors?: Array<{ msg: string }>;
}

export interface DataSourcesListResponse {
  success: boolean;
  data?: DataSource[];
  errors?: Array<{ msg: string }>;
}

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Handle body - if it's an object, stringify it
    let body = options.body;
    console.log('Original body:', body, 'Type:', typeof body);
    if (body && typeof body === 'object' && !(body instanceof FormData)) {
      body = JSON.stringify(body);
      console.log('Stringified body:', body);
    } else if (body && typeof body === 'string') {
      console.log('Body is already a string, not stringifying again');
    }
    
    const config: RequestInit = {
      ...options,
      body,
    };
    
    // Only add Content-Type header if body is not FormData
    if (!(body instanceof FormData)) {
      config.headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      };
    } else {
      config.headers = {
        ...options.headers,
      };
    }

    try {
      console.log('Making request to:', url);
      console.log('Request config:', config);
      
      const response = await fetch(url, config);
      const data = await response.json();

      console.log('Response status:', response.status);
      console.log('Response data:', data);

      if (!response.ok) {
        console.error('Request failed:', response.status, data);
        console.error('Full error details:', JSON.stringify(data, null, 2));
        throw new ApiError(
          data.errors?.[0]?.msg || data.message || data.detail?.[0]?.msg || 'Request failed',
          response.status
        );
      }

      return data;
    } catch (error) {
      console.error('Request error:', error);
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Network error', 0);
    }
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return this.request<LoginResponse>('/dmcp/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async generateToken(token: string): Promise<TokenGenerationResponse> {
    return this.request<TokenGenerationResponse>('/dmcp/users/generate-token', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/dmcp/health');
  }

  async changePassword(token: string, passwordData: ChangePasswordRequest): Promise<ChangePasswordResponse> {
    return this.request<ChangePasswordResponse>('/dmcp/users/change-password', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(passwordData),
    });
  }

  async getUserProfile(token: string): Promise<UserProfileResponse> {
    return this.request<UserProfileResponse>('/dmcp/users/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  // Datasource methods
  async getDataSources(token: string): Promise<DataSourcesListResponse> {
    return this.request<DataSourcesListResponse>('/dmcp/datasources', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async getDataSource(token: string, id: number): Promise<DataSourceResponse> {
    return this.request<DataSourceResponse>(`/dmcp/datasources/${id}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async createDataSource(token: string, dataSource: DataSourceCreateRequest): Promise<DataSourceResponse> {
    return this.request<DataSourceResponse>('/dmcp/datasources', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(dataSource),
    });
  }

  async updateDataSource(token: string, id: number, dataSource: Partial<DataSourceCreateRequest>): Promise<DataSourceResponse> {
    return this.request<DataSourceResponse>(`/dmcp/datasources/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(dataSource),
    });
  }

  async deleteDataSource(token: string, id: number): Promise<{ success: boolean; errors?: Array<{ msg: string }> }> {
    return this.request<{ success: boolean; errors?: Array<{ msg: string }> }>(`/dmcp/datasources/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async testDataSourceConnection(token: string, dataSource: DataSourceCreateRequest): Promise<{ success: boolean; errors?: Array<{ msg: string }> }> {
    return this.request<{ success: boolean; errors?: Array<{ msg: string }> }>('/dmcp/datasources/test-connection', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(dataSource),
    });
  }

  async testExistingDataSourceConnection(token: string, id: number): Promise<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }> {
    return this.request<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }>(`/dmcp/datasources/${id}/test`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  // Tool methods
  async getTools(token: string): Promise<{ success: boolean; data?: any[]; errors?: Array<{ msg: string }> }> {
    return this.request<{ success: boolean; data?: any[]; errors?: Array<{ msg: string }> }>('/dmcp/tools', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async getTool(token: string, id: number): Promise<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }> {
    return this.request<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }>(`/dmcp/tools/${id}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async createTool(token: string, tool: any): Promise<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }> {
    console.log('Creating tool with token:', token ? 'exists' : 'missing');
    console.log('Tool data:', tool);
    return this.request<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }>('/dmcp/tools', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: tool,
    });
  }

  async updateTool(token: string, id: number, tool: any): Promise<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }> {
    console.log('Updating tool with token:', token ? 'exists' : 'missing');
    console.log('Tool ID:', id);
    console.log('Tool data:', tool);
    
    const url = `${this.baseURL}/dmcp/tools/${id}`;
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tool),
    });
    
    const data = await response.json();
    console.log('Update response status:', response.status);
    console.log('Update response data:', data);
    
    if (!response.ok) {
      console.error('Update failed:', response.status, data);
      throw new ApiError(
        data.errors?.[0]?.msg || data.message || data.detail?.[0]?.msg || 'Request failed',
        response.status
      );
    }
    
    return data;
  }

  async deleteTool(token: string, id: number): Promise<{ success: boolean; errors?: Array<{ msg: string }> }> {
    const url = `${this.baseURL}/dmcp/tools/${id}`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    const data = await response.json();
    console.log('Delete response status:', response.status);
    console.log('Delete response data:', data);
    
    if (!response.ok) {
      console.error('Delete failed:', response.status, data);
      throw new ApiError(
        data.errors?.[0]?.msg || data.message || data.detail?.[0]?.msg || 'Request failed',
        response.status
      );
    }
    
    return data;
  }

  async executeTool(token: string, id: number, parameters: any = {}): Promise<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }> {
    console.log('Executing tool with token:', token ? 'exists' : 'missing');
    console.log('Tool ID:', id, 'Parameters:', parameters);
    return this.request<{ success: boolean; data?: any; errors?: Array<{ msg: string }> }>(`/dmcp/tools/${id}/execute`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: { parameters },
    });
  }

}

export const apiService = new ApiService();
export { ApiError };
