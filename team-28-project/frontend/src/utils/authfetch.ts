// utils/authorizedFetch.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:3000'; 

/**
 * Wrapper for fetch() that automatically attaches the saved auth token.
 * Use this for any request that requires user authentication.
 */
export async function authorizedFetch(url: string, options: RequestInit = {}) {
  try {
    const token = await AsyncStorage.getItem('authToken');

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Merge existing headers
    if (options.headers) {
      Object.assign(headers, options.headers);
    }

    // Add auth token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // 🟡 Fix: Attach base URL manually
    return fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
    });
  } catch (error) {
    console.error('Error in authorizedFetch:', error);
    throw error;
  }
}
