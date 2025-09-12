/**
 * Data Fetching Hooks
 * 
 * Professional data management with React Query patterns
 * Senior pattern: Custom hooks for reusable data logic
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, ApiError } from '../services/api';

// Generic hook for API calls with loading and error states
export function useApiCall<T>(
  apiFunction: () => Promise<T>,
  dependencies: any[] = [],
  options: {
    immediate?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: ApiError) => void;
  } = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const mountedRef = useRef(true);

  const execute = useCallback(async () => {
    if (!mountedRef.current) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const result = await apiFunction();
      if (mountedRef.current) {
        setData(result);
        options.onSuccess?.(result);
      }
    } catch (err) {
      if (mountedRef.current) {
        const apiError = err instanceof ApiError ? err : new ApiError(500, 'Unknown error');
        setError(apiError);
        options.onError?.(apiError);
      }
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [apiFunction, options, ...dependencies]);

  useEffect(() => {
    mountedRef.current = true;
    
    if (options.immediate !== false) {
      execute();
    }

    return () => {
      mountedRef.current = false;
    };
  }, [execute, options.immediate]);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return {
    data,
    isLoading,
    error,
    refetch: execute,
  };
}

// Hook specifically for exams data
export function useExams() {
  return useApiCall(
    () => apiClient.getPublicExams(),
    [],
    {
      onError: (error) => {
        console.error('Failed to fetch exams:', error.message);
      },
    }
  );
}

// Hook specifically for user exams data
export function useUserExams() {
  return useApiCall(
    () => apiClient.getUserExams(),
    [],
    {
      onError: (error) => {
        console.error('Failed to fetch user exams:', error.message);
      },
    }
  );
}

// Hook for managing async operations with better UX
export function useAsyncOperation<T = any>() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const execute = useCallback(async (
    operation: () => Promise<T>,
    options: {
      successMessage?: string;
      onSuccess?: (result: T) => void;
      onError?: (error: ApiError) => void;
    } = {}
  ) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await operation();
      
      if (options.successMessage) {
        setSuccess(options.successMessage);
      }
      
      options.onSuccess?.(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      
      if (err instanceof ApiError) {
        options.onError?.(err);
      }
      
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  return {
    isLoading,
    error,
    success,
    execute,
    clearMessages,
  };
}

// Hook for debounced values (useful for search)
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Hook for local storage with type safety
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}
