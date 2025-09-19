// file: services/auth.service.ts

import {webApiClient} from '../libs/utils/apiClient';
import { setAuthData, clearAuthData, getAccessToken } from '../libs/utils/auth.utils';
import { AuthResponse, LoginRequest, RegisterRequest } from '../libs/types';

class AuthService {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await webApiClient<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    setAuthData(response);
    return response;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await webApiClient<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    setAuthData(response);
    return response;
  }

  async logout(): Promise<void> {
    try {
      if (getAccessToken()) {
        await webApiClient('/auth/logout', { method: 'POST' });
      }
    } catch (error) {
      console.warn('Logout request to the server failed, clearing local data anyway.');
    } finally {
      clearAuthData();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  }

  isAuthenticated(): boolean {
    return !!getAccessToken();
  }
}

export const authService = new AuthService();