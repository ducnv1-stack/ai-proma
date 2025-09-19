// file: src/types/auth.types.ts
import { User } from './user.types';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
  username?: string;
}

// Chúng ta sẽ thống nhất dùng LoginResponse và bỏ AuthResponse để tránh trùng lặp
export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_in?: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}