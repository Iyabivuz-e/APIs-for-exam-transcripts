/**
 * API Service Layer
 * 
 * Simple, secure, and reusable API client
 * Senior pattern: Centralized API logic with error handling
 */

import { LoginRequest, TokenResponse, User, Exam, UserExam, CreateExamData } from '../types';

// Base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Simple HTTP client with authentication
 * Keeps token in memory for simplicity (can be enhanced later)
 */
class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    // Try to restore token from localStorage on initialization
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Set up headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };
    
    // Add authentication header if token exists
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle API errors consistently
        throw new ApiError(
          response.status,
          data.message || `HTTP ${response.status}`
        );
      }

      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle network errors
      throw new ApiError(0, 'Network error occurred');
    }
  }

  // Authentication methods
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await this.request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    // Store token after successful login
    this.setToken(response.access_token);
    return response;
  }

  async logout(): Promise<void> {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } finally {
      // Always clear token, even if API call fails
      this.setToken(null);
    }
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.request<{ user: User; permissions: any }>('/auth/me');
    return response.user;
  }

  async refreshToken(): Promise<TokenResponse> {
    const response = await this.request<TokenResponse>('/auth/refresh', {
      method: 'POST',
    });
    this.setToken(response.access_token);
    return response;
  }

  // Exam methods
  async getPublicExams(filters?: { 
    title?: string; 
    date_from?: string; 
    date_to?: string; 
    sort_by?: 'date' | 'title'; 
    order?: 'asc' | 'desc' 
  }): Promise<Exam[]> {
    let endpoint = '/public/exams';
    
    if (filters) {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      if (params.toString()) {
        endpoint += `?${params.toString()}`;
      }
    }
    
    const response = await this.request<{exams: Exam[], pagination: any}>(endpoint);
    return response.exams || [];
  }

  async getUserExams(): Promise<UserExam[]> {
    const response = await this.request<{exams: UserExam[], statistics?: any}>('/private/users/me/exams');
    return response.exams || [];
  }

  async submitVote(examId: number, vote: number): Promise<void> {
    return this.request(`/private/users/exams/${examId}/vote`, {
      method: 'POST',
      body: JSON.stringify({ vote }),
    });
  }

  // Register for an exam (User only)
  async registerForExam(examId: number): Promise<any> {
    return this.request(`/private/users/exams/${examId}/register`, {
      method: 'POST',
    });
  }

  // Admin methods (only for admin users)
  async createExam(examData: CreateExamData): Promise<Exam> {
    return this.request<Exam>('/private/admin/exams', {
      method: 'POST',
      body: JSON.stringify(examData),
    });
  }

  async deleteExam(examId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/private/admin/exams/${examId}`, {
      method: 'DELETE',
    });
  }

  async getUsers(): Promise<User[]> {
    return this.request<User[]>('/private/admin/users');
  }

  // Assign user to exam (Admin only)
  async assignUserToExam(examId: number, userId: number): Promise<any> {
    return this.request(`/private/admin/exams/${examId}/assign-user?user_id=${userId}`, {
      method: 'POST',
    });
  }

  // Supervisor methods (only for supervisor users)
  async assignVote(examId: number, voteData: { user_id: number; vote: number }): Promise<any> {
    return this.request(`/private/supervisor/exams/${examId}/vote`, {
      method: 'PUT',
      body: JSON.stringify({
        user_id: voteData.user_id,
        exam_id: examId,
        vote: voteData.vote
      }),
    });
  }

  // Get ungraded assignments for supervisors
  async getUngradedAssignments(): Promise<any[]> {
    const response = await this.request<{assignments: any[], success: boolean, total: number}>('/private/supervisor/ungraded-assignments');
    return response.assignments || [];
  }

  // Check if a specific user has any ungraded exams available for voting
  async checkUserHasUngradedExams(userId: number): Promise<boolean> {
    try {
      const ungradedAssignments = await this.getUngradedAssignments();
      const userAssignments = ungradedAssignments.filter((assignment: any) => 
        assignment.user_id === userId
      );
      return userAssignments.length > 0;
    } catch (error) {
      return false;
    }
  }

  // Get exam assignments for supervisor to grade (legacy - might not be used)
  async getExamAssignments(examId?: number): Promise<UserExam[]> {
    const endpoint = examId ? `/private/supervisor/exams/${examId}/assignments` : '/private/supervisor/assignments';
    const response = await this.request<{assignments: UserExam[]}>(endpoint);
    return response.assignments || [];
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export { ApiError };
