import axios, { AxiosResponse } from 'axios';
import { 
  AuthTokens, 
  LoginCredentials, 
  RegisterData, 
  User, 
  UserPermissions 
} from '../types/auth';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
const authApi = axios.create({
  baseURL: `${API_BASE_URL}/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const TOKEN_KEY = 'genai_access_token';
const REFRESH_TOKEN_KEY = 'genai_refresh_token';

export const tokenManager = {
  getToken: (): string | null => localStorage.getItem(TOKEN_KEY),
  getRefreshToken: (): string | null => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens: (tokens: AuthTokens): void => {
    localStorage.setItem(TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  },
  clearTokens: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

// Request interceptor to add auth token
authApi.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = tokenManager.getRefreshToken();
        if (refreshToken) {
          const response = await authApi.post('/refresh', {
            refresh_token: refreshToken,
          });
          
          const tokens: AuthTokens = response.data;
          tokenManager.setTokens(tokens);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
          return authApi(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        tokenManager.clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  // Authentication methods
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await authApi.post('/login', credentials);
    const tokens = response.data;
    tokenManager.setTokens(tokens);
    return tokens;
  },

  async register(data: RegisterData): Promise<User> {
    const response: AxiosResponse<User> = await authApi.post('/register', data);
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await authApi.post('/logout');
    } catch (error) {
      // Even if logout fails on server, clear local tokens
      console.error('Logout error:', error);
    } finally {
      tokenManager.clearTokens();
    }
  },

  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = tokenManager.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response: AxiosResponse<AuthTokens> = await authApi.post('/refresh', {
      refresh_token: refreshToken,
    });
    
    const tokens = response.data;
    tokenManager.setTokens(tokens);
    return tokens;
  },

  // User information methods
  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await authApi.get('/me');
    return response.data;
  },

  async getUserPermissions(): Promise<{ user_id: number; username: string; permissions: UserPermissions }> {
    const response = await authApi.get('/me/permissions');
    return response.data;
  },

  async verifyToken(): Promise<{ valid: boolean; user_id: number; username: string }> {
    const response = await authApi.get('/verify-token');
    return response.data;
  },

  // Password management
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await authApi.post('/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  async initiatePasswordReset(email: string): Promise<{ message: string; reset_token?: string }> {
    const response = await authApi.post('/password-reset/initiate', { email });
    return response.data;
  },

  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    await authApi.post('/password-reset/confirm', {
      token,
      new_password: newPassword,
    });
  },

  // Utility methods
  isAuthenticated(): boolean {
    return !!tokenManager.getToken();
  },

  hasValidTokens(): boolean {
    const accessToken = tokenManager.getToken();
    const refreshToken = tokenManager.getRefreshToken();
    return !!(accessToken && refreshToken);
  },
};

export default authService; 