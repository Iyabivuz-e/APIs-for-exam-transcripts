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
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'LOGIN_START':
      return { ...state, isLoading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'LOGIN_ERROR':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
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
      const token = localStorage.getItem('auth_token'); // Fixed: Use same key as api.ts
      
      if (token) {
        try {
          // Set token in api client first
          apiClient.setToken(token);
          const user = await apiClient.getCurrentUser();
          dispatch({ type: 'LOGIN_SUCCESS', payload: user });
        } catch (error) {
          // Clear invalid token
          localStorage.removeItem('auth_token');
          apiClient.setToken(null);
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginRequest) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await apiClient.login(credentials);
      dispatch({ type: 'LOGIN_SUCCESS', payload: response.user });
    } catch (error) {
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
      // Continue with logout even if API call fails
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
