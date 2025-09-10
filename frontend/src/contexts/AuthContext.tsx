/**
 * Authentication Context
 * 
 * Simple state management for user authentication
 * Senior pattern: Context + Reducer for predictable state
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { User, LoginRequest } from '../types';
import { apiClient, ApiError } from '../services/api';

// State shape
interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

// Actions
type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean };

// Initial state
const initialState: AuthState = {
  user: null,
  isLoading: true, // Start as loading to check for existing session
  error: null,
  isAuthenticated: false,
};

// Simple reducer - easy to understand and debug
function authReducer(state: AuthState, action: AuthAction): AuthState {
  console.log('🔄 Auth reducer:', action.type, action);
  
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    
    case 'LOGIN_SUCCESS':
      console.log('✅ LOGIN_SUCCESS - User logged in:', action.payload.email);
      return {
        ...state,
        user: action.payload,
        isLoading: false,
        error: null,
        isAuthenticated: true,
      };
    
    case 'LOGIN_ERROR':
      return {
        ...state,
        user: null,
        isLoading: false,
        error: action.payload,
        isAuthenticated: false,
      };
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        error: null,
        isLoading: false,
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    
    default:
      return state;
  }
}

// Context interface
interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = apiClient.getToken();
      console.log('🔍 Auth check - Token found:', !!token);
      
      if (token) {
        try {
          // Verify token is still valid by fetching current user
          const user = await apiClient.getCurrentUser();
          console.log('✅ Auth restored for user:', user.email);
          dispatch({ type: 'LOGIN_SUCCESS', payload: user });
        } catch (error) {
          // Token is invalid or expired
          console.warn('❌ Stored token is invalid:', error);
          apiClient.setToken(null);
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        // No token found
        console.log('ℹ️ No token found, setting loading to false');
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    // Add a small delay to ensure DOM is ready
    const timeoutId = setTimeout(checkAuth, 100);
    
    return () => clearTimeout(timeoutId);
  }, []);

  // Login function
  const login = async (credentials: LoginRequest) => {
    console.log('🚀 Login attempt for:', credentials.email);
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await apiClient.login(credentials);
      console.log('✅ Login successful, user:', response.user.email);
      dispatch({ type: 'LOGIN_SUCCESS', payload: response.user });
    } catch (error) {
      console.error('❌ Login failed:', error);
      const message = error instanceof ApiError 
        ? error.message 
        : 'Login failed. Please try again.';
      dispatch({ type: 'LOGIN_ERROR', payload: message });
      throw error; // Re-throw so components can handle it
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await apiClient.logout();
    } catch (error) {
      // Log error but continue with logout
      console.warn('Logout API call failed:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook for using auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
