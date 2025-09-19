// Common API types used across services

// API Response Types
export interface ContentPlanQueryParams {
  limit?: number;
  offset?: number;
  status?: string;
  channel_type?: string;
  product?: string;
  target_customer?: string;
}
export interface ApiResponse<T> {
  success: boolean;
  tag: string;
  code: number;
  data: T;
  message?: string;
}

export interface ApiError {
  success: false;
  tag: string;
  message: string;
  code: number;
}

// Pagination types
export interface PaginationParams {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Paginated API Response Types
export interface PaginatedApiResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    has_more?: boolean;
  };
}

// Query parameters for paginated requests
export interface PaginatedQueryParams {
  limit?: number;
  offset?: number;
  page?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

// Generic filter interface
export interface BaseFilter {
  search?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}

// Common status types
export type CommonStatus = 'active' | 'inactive' | 'pending' | 'completed' | 'cancelled';

// Sort order type
export type SortOrder = 'asc' | 'desc';
