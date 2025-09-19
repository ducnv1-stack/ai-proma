// file: src/types/user.types.ts

export interface User {
  id: string;
  email: string;
  name: string;
  role?: string;
  picture?: string;
  provider?: string;
  credit?: number;
  status?: string;
  email_verified?: boolean;
  created_at?: string;
  avatar?: string;
  createdAt?: Date;
  lastLoginAt?: Date;
  subscription?: {
    plan: 'free' | 'pro' | 'enterprise';
    status: 'active' | 'cancelled' | 'expired';
    expiresAt?: Date;
  };
}

export interface UpdateUserRequest {
  name?: string;
  username?: string;
  avatar?: string;
}