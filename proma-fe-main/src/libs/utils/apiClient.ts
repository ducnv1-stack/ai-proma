// file: lib/apiClient.ts

import { getAccessToken, getRefreshToken, handleUnauthorized, setAuthData } from './auth.utils';
import { ApiError } from './ApiError';
import { AuthResponse } from '../types';

// --- Các hàm helper và biến quản lý queue giữ nguyên ---

let isRefreshing = false;
let failedQueue: Array<{ resolve: (value: unknown) => void; reject: (reason?: any) => void; }> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

const parseErrorBody = async (response: Response): Promise<any> => {
  try {
    return await response.clone().json();
  } catch (e) {
    return await response.text();
  }
};

// --- BẮT ĐẦU PHẦN TÁI CẤU TRÚC ---

/**
 * Định nghĩa cấu hình cho mỗi instance của API client.
 */
interface ApiClientConfig {
  baseUrl: string;
  // Bật/tắt logic refresh token cho từng instance
  useRefreshTokenLogic?: boolean;
  // Bật/tắt việc tự động đính kèm access token
  useAuthToken?: boolean;
}

/**
 * Hàm "nhà máy" (Factory) để tạo ra một instance của apiClient.
 * @param config - Cấu hình cho instance (baseUrl, có dùng refresh token không, etc.)
 * @returns Một hàm apiClient đã được cấu hình sẵn.
 */
const createApiClient = (config: ApiClientConfig) => {
  // Trả về một hàm async, đây chính là client instance của chúng ta
  return async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
    const token = getAccessToken();
    const url = `${config.baseUrl}${endpoint}`; // Sử dụng baseUrl từ config

    const headers = new Headers(options.headers || {});
    headers.set('accept', 'application/json');
    if (options.body) {
      headers.set('Content-Type', 'application/json');
    }

    // Chỉ đính kèm token nếu được cấu hình
    if (config.useAuthToken && token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
      // Chỉ thực hiện logic refresh token nếu được bật và lỗi là 401
      if (config.useRefreshTokenLogic && response.status === 401) {
        // --- Logic refresh token giữ nguyên y hệt như trước ---
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          }).then(() => createApiClient(config)<T>(endpoint, options)) // Gọi lại chính nó
            .catch(err => Promise.reject(err));
        }

        isRefreshing = true;
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
          handleUnauthorized();
          return Promise.reject(new ApiError(401, 'Unauthorized', { message: 'No refresh token available.' }));
        }
        
        try {
          // Lưu ý: Endpoint refresh token luôn thuộc về WebService
          const webServiceBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://superbai.io/api';
          const refreshResponse = await fetch(`${webServiceBaseUrl}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
          });

          if (!refreshResponse.ok) {
            const errorBody = await parseErrorBody(refreshResponse);
            throw new ApiError(refreshResponse.status, refreshResponse.statusText, errorBody);
          }

          const newAuthData: AuthResponse = await refreshResponse.json();
          setAuthData(newAuthData);
          processQueue(null, newAuthData.access_token);
          
          return createApiClient(config)<T>(endpoint, options); // Gọi lại chính nó

        } catch (error) {
          processQueue(error as Error, null);
          handleUnauthorized();
          return Promise.reject(error);
        } finally {
          isRefreshing = false;
        }
        // --- Kết thúc logic refresh token ---
      }

      // Với các lỗi khác, ném ra ApiError
      const errorBody = await parseErrorBody(response);
      throw new ApiError(response.status, response.statusText, errorBody);
    }

    if (response.status === 204) return null as T;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }
    return response.text() as T;
  };
};

// --- TẠO VÀ EXPORT CÁC INSTANCE CỤ THỂ ---

/**
 * Client để giao tiếp với WebService chính.
 * Có hỗ trợ tự động refresh token.
 */
export const webApiClient = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://superbai.io/api',
  useRefreshTokenLogic: true,
  useAuthToken: true,
});

/**
 * Client để giao tiếp với AI Service.
 * Không cần logic refresh token và không tự đính kèm token (vì AI.service.ts sẽ tự cung cấp token riêng).
 */
export const aiApiClient = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_AI_SERVICE_URL || 'https://aiapi.superbai.io/api/v1',
  useRefreshTokenLogic: false,
  useAuthToken: false, // Để AI.service.ts tự quản lý header Authorization
});

