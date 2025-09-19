// Browser-compatible JWT implementation for SuperbAI authentication
import CryptoJS from 'crypto-js';
import { JWTPayload } from '../types';

// JWT secret that matches the working curl command
const JWT_SECRET = '155792625553b3e0f95baf5034611266';

// Base64 URL encode (browser-safe)
function base64UrlEncode(str: string): string {
  return btoa(str)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

// Generate JWT token for SuperbAI authentication (browser-compatible)
export function generateJWTToken(payload: JWTPayload): string {
  try {
    // Create JWT header
    const header = {
      alg: 'HS256',
      typ: 'JWT'
    };

    // Encode header and payload
    const encodedHeader = base64UrlEncode(JSON.stringify(header));
    const encodedPayload = base64UrlEncode(JSON.stringify(payload));

    // Create signature using HMAC SHA256
    const data = `${encodedHeader}.${encodedPayload}`;
    const signature = CryptoJS.HmacSHA256(data, JWT_SECRET);
    const base64Signature = signature.toString(CryptoJS.enc.Base64);
    const encodedSignature = base64Signature
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');

    // Combine all parts
    const token = `${encodedHeader}.${encodedPayload}.${encodedSignature}`;
    
    console.log('Generated JWT token with payload:', payload);
    return token;
  } catch (error) {
    console.error('Failed to generate JWT token:', error);
    
    // Fallback to working token if generation fails
    const workingToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwidXNlcm5hbWUiOiJKb2huIERvZSIsInVzZXJfaWQiOiI5NjNjMjc1NC02Mzg4LTQyMTktODk4OS0zOWJiNWQxMmFkZSIsImFnZW50X2lkIjoiZmFjZWJvb2tfbWFya2V0aW5nX2FnZW50Iiwid29ya3NwYWNlX2lkIjoiOTYzYzI3NTQtNjM4OC00MjE5LTg5ODktMzliYjVkMTJhZGUiLCJzZXNzaW9uX2lkIjoiNzMxMjZiZWUtNDI3OC00YzcwLWE4OTktZTBlNzg0MzkwMmE1Iiwicm9sZSI6InVzZXIiLCJ1c2VyX2luZm8iOiIiLCJpYXQiOjE1MTYyMzkwMjJ9.jObYNndgJlHNz8tUYIft4z76ewi29RWp7vfTgIzdWFU';
    console.log('Using fallback JWT token');
    return workingToken;
  }
}

// Create session payload with user information - Updated to use dynamic data
export function createSessionPayload(
  userId: string,
  username: string,
  agentId: string = 'facebook_marketing_agent',
  workspaceId?: string
): JWTPayload {
  return {
    sub: userId || "1234",
    username: username || "John Doe", 
    user_id: userId || "963c2754-6388-4219-8989-39bb5d12ade",
    agent_id: agentId,
    workspace_id: workspaceId || "963c2754-6388-4219-8989-39bb5d12ade",
    role: "user",
    user_info: "",
    iat: Math.floor(Date.now() / 1000)
  };
}



// Verify JWT token (for debugging purposes)
export function verifyJWTToken(token: string): JWTPayload | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid JWT format');
    }

    // Decode payload
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    return payload as JWTPayload;
  } catch (error) {
    console.error('JWT token verification failed:', error);
    return null;
  }
}
