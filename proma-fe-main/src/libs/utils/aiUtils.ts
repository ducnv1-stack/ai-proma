import { createSessionPayload, generateJWTToken } from './jwt';

export interface AIServiceConfig {
  baseURL: string;
  apiKey: string;
}

export interface UserInfo {
  id: string;
  name: string;
}

/**
 * Generate JWT token for AI service authentication
 */
export function getAIServiceToken(
  currentUser: UserInfo | null,
  userId?: string,
  username?: string
): string {
  const actualUserId = userId || currentUser?.id || '';
  const actualUsername = username || currentUser?.name || '';
  
  const payload = createSessionPayload(
    actualUserId,
    actualUsername,
    'facebook_marketing_agent'
  );

  return generateJWTToken(payload);
}

/**
 * Make a basic request to AI service
 */
export async function makeAIRequest<T>(
  config: AIServiceConfig,
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${config.baseURL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      ...(config.apiKey && { 'Authorization': `Bearer ${config.apiKey}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`AI Service Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Make an authenticated request to AI service with JWT token
 */
export async function makeAuthenticatedAIRequest<T>(
  config: AIServiceConfig,
  currentUser: UserInfo | null,
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  if (!currentUser) {
    throw new Error('User not authenticated. Please create a session first.');
  }

  const jwtToken = getAIServiceToken(currentUser);
  const url = `${config.baseURL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwtToken}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`AI Service Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
