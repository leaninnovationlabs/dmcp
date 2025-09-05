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
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new ApiError(
          data.errors?.[0]?.msg || data.message || 'Request failed',
          response.status
        );
      }

      return data;
    } catch (error) {
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
}

export const apiService = new ApiService();
export { ApiError };
